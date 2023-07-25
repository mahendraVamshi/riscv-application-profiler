
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
import riscv_config.isa_validator as isaval
from riscv_application_profiler.utils import Utilities

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
    logger.info(f'Parsed {len(cl_matches_list)} instructions.')
    logger.info("Decoding...")
    isac_decoder = disassembler()
    isac_decoder.setup(arch='rv64')
    master_inst_list = []
    for entry in cl_matches_list:
        if entry.instr is None:
            continue
        temp_entry = isac_decoder.decode(entry)
        master_inst_list.append(temp_entry)

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
    ]

    (extension_list, err, err_list) = isaval.get_extension_list(isa)

    for e in err_list:
        logger.error(e)
    if err:
        raise SystemExit(1)
    
    isa_arg = isa.split('I')[0]

    mode_list, mode_dict = instr_groups.privilege_modes(log)

    op_lists,ops_count, extension_instruction_list, op_dict = instr_groups.group_by_operation(groups, isa_arg, extension_list, master_inst_list)
    if (len(extension_instruction_list)!=len(master_inst_list)):
        # left_out=[]
        # for i in master_inst_list:
        #     if i not in extension_instruction_list:
        #         left_out.append(i)
        #         print(i)
        logger.warning("Check the extension input.")

    curr_ops_dict = utils.compute_ops_dict(args_list=groups, isa_arg=isa_arg, ext_list=extension_list)

    # Group by branch sizes
    branch_threshold = branch_ops.compute_threshold(master_inst_list=extension_instruction_list, ops_dict=op_dict)
    size_list, size_dict = branch_ops.group_by_branch_offset(master_inst_list=extension_instruction_list, ops_dict=op_dict, branch_threshold=branch_threshold)

    # Group by branch signs
    b_direc_list, b_direc_dict = branch_ops.group_by_branch_sign(master_inst_list=extension_instruction_list, ops_dict=op_dict)

    #ananlyses of cache
    data_cache_list, data_cache_dict=cache.data_cache_simulator(extension_instruction_list, op_dict)
    instruction_cache_list,instruction_cache_dict=cache.instruction_cache_simulator(master_inst_list)

    #ananlyses of loops
    loop_list, loop_instr_dict = branch_ops.loop_compute(master_inst_list=extension_instruction_list, ops_dict=op_dict)

    #ananlyses of registers
    reg_list, regs_dict = register_compute.register_compute(master_inst_list=extension_instruction_list)

    #ananlyses of floating point registers
    F_reg_list, F_regs_dict = register_compute.fregister_compute(master_inst_list=extension_instruction_list,extension_list=extension_list)

    #ananlyses of jumps
    j_direc_list, j_direc_dict = jumps_ops.jumps_comput(master_inst_list=extension_instruction_list, ops_dict=op_dict)

    #ananlyses of jumps size
    jump_list,jump_instr_dict = jumps_ops.jump_size(master_inst_list=extension_instruction_list, ops_dict=op_dict)

    #ananlyses of dependancy(raw)
    raw_instruction_list, raw_dict = dependency.raw_compute(master_inst_list=extension_instruction_list)

    #ananlyses of csr
    csr_reg_list, csr_dict = csr_compute.csr_compute(master_inst_list=extension_instruction_list, ops_dict=op_dict)

    #ananlyses of store load bypass
    load_address_list,bypass_dict = store_load_bypass.store_load_bypass(extension_instruction_list, op_dict)
    
    
    if 'C' in extension_list:
        logger.warning("riscv-isac does not decode immediate fields for compressed instructions. \
Value based metrics on branch ops may be inaccurate.")

    utils.tabulate_stats1(op_lists,ops_count, header_name="Operation", metric_name="Grouping Instructions by Type of Operation.")
    utils.tabulate_stats1(mode_list, mode_dict, header_name="Privilaged modes", metric_name="Grouping Instructions by Privilege Mode.")
    utils.tabulate_stats1(size_list, size_dict, header_name='Size',metric_name="Grouping Branches by Offset Size.")
    utils.tabulate_stats1(b_direc_list, b_direc_dict, header_name='Direction',metric_name="Grouping Branches by Direction.")
    utils.tabulate_stats1(loop_list, loop_instr_dict, header_name='Instruction Name',metric_name="Nested loop Computation.")
    utils.tabulate_stats1(reg_list, regs_dict, header_name='Register Name',metric_name="Register Computation.")
    utils.tabulate_stats1(F_reg_list, F_regs_dict, header_name='fRegister Name',metric_name="Floating Point Register Computation.")
    utils.tabulate_stats1(j_direc_list, j_direc_dict, header_name='Direction',metric_name="Jumps Computation.")
    utils.tabulate_stats1(jump_list,jump_instr_dict, header_name='Name',metric_name="Jumps Size.")
    utils.tabulate_stats1(data_cache_list, data_cache_dict, header_name='Data Cache',metric_name="Data Cache Computation.")
    utils.tabulate_stats1(instruction_cache_list, instruction_cache_dict, header_name='Instruction Cache',metric_name="Instruction Cache Computation.")
    utils.tabulate_stats1(raw_instruction_list, raw_dict, header_name='Dependant Instructions',metric_name="Reads after Writes(RAW) Computation.")
    utils.tabulate_stats1(csr_reg_list, csr_dict, header_name='CSR Register(s)',metric_name="CSR Computation.")
    utils.tabulate_stats1(load_address_list,bypass_dict, header_name='Address',metric_name="Store load bypass")