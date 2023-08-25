
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
from riscv_isac.log import *
from riscv_isac.plugins.spike import *
from riscv_application_profiler.plugins import instr_groups
from riscv_application_profiler.plugins import branch_ops
from riscv_application_profiler.plugins import register_compute
from riscv_application_profiler.plugins import cache
from riscv_application_profiler.plugins import jumps_ops
from riscv_application_profiler.plugins import dependency
from riscv_application_profiler.plugins import csr_compute
from riscv_application_profiler.plugins import store_load_bypass
from riscv_application_profiler.plugins import pattern
import riscv_config.isa_validator as isaval
from riscv_application_profiler.utils import Utilities
import os
import yaml

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'config.yaml')
with open(consts.config_path, 'r') as config_file:
   
    config = yaml.safe_load(config_file)

def print_stats(op_dict, counts):
    '''
    Prints the statistics of the grouped instructions.

    Args:
        - op_dict: A dictionary with the operations as keys and a list of InstructionEntry
            objects as values.
        - counts: A dictionary with the operations as keys and the number of instructions
            in each group as values.
    '''
    logger.info("Printing statistics.")
    for op in op_dict.keys():
        logger.info(f'{op}: {counts[op]}')
    logger.info("Done.")

def run(log, isa, output, verbose):
    from build.lib.rvopcodesdecoder import disassembler
    spike_parser = spike()
    spike_parser.setup(trace=str(log), arch='rv64')
    iter_commitlog = spike_parser.__iter__()
    with open(log, 'r') as logfile:
        # Read the log file
        lines = logfile.readlines()
        cl_matches_list = [iter_commitlog.__next__() for i in range(len(lines))]
    isac_decoder = disassembler()
    isac_decoder.setup(arch='rv64')
    master_inst_list = []
    for entry in cl_matches_list:
        if entry.instr is None:
            continue
        # print(entry)
        temp_entry = isac_decoder.decode(entry)
        master_inst_list.append(temp_entry)
        # if entry.instr == 57378 or entry.instr == 58374 or entry.instr == 62510 or entry.instr == 63538 or entry.instr == 64566 or entry.instr == 60422 or entry.instr == 57530 or entry.instr == 58558 or entry.instr == 59586 or entry.instr == 60614 or entry.instr == 58394 or entry.instr == 62114 or entry.instr == 61094:
        #     print(temp_entry)
    
    logger.info(f'Parsed {len(master_inst_list)} instructions.')
    logger.info("Decoding...")
    logger.info("Done decoding instructions.")
    logger.info("Starting to profile...")
    
    utils = Utilities(log, output)
    utils.metadata()

    # Grouping by operations
    groups = [
        'loads',
        'stores',
        'imm computes',
        'imm shifts',
        'reg computes',
        'reg shifts',
        'jumps',
        'branches',
        "compares",
        "conversions",
        "moves",
        "classifies",
        "csrs",
        "fence",
    ]

    (extension_list, err, err_list) = isaval.get_extension_list(isa)

    for e in err_list:
        logger.error(e)
    if err:
        raise SystemExit(1)
    
    isa_arg = isa.split('I')[0]

    ret_dict, extension_instruction_list, op_dict = instr_groups.group_by_operation(groups, isa_arg, extension_list, master_inst_list)
    if (len(extension_instruction_list)<=len(master_inst_list)):
        # left_out=[]
        # for i in master_inst_list:
        #     if i not in extension_instruction_list:
        #         left_out.append(i)
        #         print(i)
        logger.warning("Check the extension input.")

    curr_ops_dict = utils.compute_ops_dict(args_list=groups, isa_arg=isa_arg, ext_list=extension_list) 
    
    if 'C' in extension_list:
        logger.warning("riscv-isac does not decode immediate fields for compressed instructions. \
Value based metrics on branch ops may be inaccurate.")


    if 'cfg' in config['profiles']:
        metrics = config['profiles']['cfg']['metrics']
        if 'instr_groups' in metrics:
            utils.tabulate_stats_dict(ret_dict, header_name="Grouping Instructions by Type of Operation.")

            # Group by privilege modes
            ret_dict1 = instr_groups.privilege_modes(log)
            utils.tabulate_stats_dict(ret_dict1, header_name="Grouping Instructions by Privilege Mode.")
        if 'branch_ops' in metrics:
            # Group by branch sizes
            branch_threshold = branch_ops.compute_threshold(master_inst_list=extension_instruction_list, ops_dict=op_dict)
            ret_dict1 = branch_ops.group_by_branch_offset(master_inst_list=extension_instruction_list, ops_dict=op_dict, branch_threshold=branch_threshold)
            # Group by branch signs
            ret_dict2 = branch_ops.group_by_branch_sign(master_inst_list=extension_instruction_list, ops_dict=op_dict)
            #analysis of loops
            ret_dict3 = branch_ops.loop_compute(master_inst_list=extension_instruction_list, ops_dict=op_dict)

            utils.tabulate_stats_dict(ret_dict1, header_name="Grouping Branches by Offset Size.")
            utils.tabulate_stats_dict(ret_dict2, header_name="Grouping Branches by Direction.")
            utils.tabulate_stats_dict(ret_dict3, header_name="Nested loop Computation.")
        if 'register_compute' in metrics:
            #analysis of registers
            ret_dict1 = register_compute.register_compute(master_inst_list=extension_instruction_list)

            #analysis of floating point registers
            ret_dict2 = register_compute.fregister_compute(master_inst_list=extension_instruction_list,extension_list=extension_list)

            utils.tabulate_stats_dict(ret_dict1, header_name="Register Computation.")
            utils.tabulate_stats_dict(ret_dict2, header_name="Floating Point Register Computation.")
        if 'jumps_ops' in metrics:
            #analysis of jumps
            ret_dict1 = jumps_ops.jumps_comput(master_inst_list=extension_instruction_list, ops_dict=op_dict)

            #analysis of jumps size
            jump_list,jump_instr_dict = jumps_ops.jump_size(master_inst_list=extension_instruction_list, ops_dict=op_dict)
            utils.tabulate_stats_dict(ret_dict1, header_name="Jump Direction.")
            utils.tabulate_stats1(jump_list,jump_instr_dict, header_name='Name',metric_name="Jumps Size.")
        if 'cache' in metrics:
            #analysis of cache
            ret_dict1=cache.data_cache_simulator(extension_instruction_list, op_dict)
            ret_dict2=cache.instruction_cache_simulator(master_inst_list)

            utils.tabulate_stats_dict(ret_dict1, header_name="Data Cache Utilization.")
            utils.tabulate_stats_dict(ret_dict2, header_name="Instruction Cache Utilization.")
        if 'dependency' in metrics:
            #analysis of dependancy(raw)
            ret_dict1 = dependency.raw_compute(master_inst_list=extension_instruction_list)

            utils.tabulate_stats_dict(ret_dict1, header_name="Reads after Writes(RAW) Computation.")
        if 'csr_compute' in metrics:
            #analysis of csr
            ret_dict1 = csr_compute.csr_compute(master_inst_list=extension_instruction_list, ops_dict=op_dict)

            utils.tabulate_stats_dict(ret_dict1, header_name="CSR Computation.")
        if 'store_load_bypass' in metrics:
            #analysis of store load bypass
            ret_dict1 = store_load_bypass.store_load_bypass(extension_instruction_list, op_dict)
            utils.tabulate_stats_dict(ret_dict1, header_name="Store load bypass")
        if 'pattern' in metrics:
            #analysis of pattern
            ret_dict1=pattern.group_by_pattern(master_inst_list)
            utils.tabulate_stats_dict(ret_dict1, header_name="Pattern")

