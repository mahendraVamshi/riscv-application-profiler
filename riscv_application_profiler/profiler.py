
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
    #print (extension_list)
    for e in err_list:
        logger.error(e)
    if err:
        raise SystemExit(1)
    
    isa_arg = isa.split('I')[0]

   # groups = list(ops_dict.keys())

    op_dict1, counts1 = instr_groups.group_by_operation(groups, isa_arg, extension_list, master_inst_list)
    #print_stats(op_dict1, counts1)

    op_dict, counts = instr_groups.privilege_modes(log)

    curr_ops_dict = utils.compute_ops_dict(args_list=groups, isa_arg=isa_arg, ext_list=extension_list)

    # Group by branch sizes
    branch_threshold = branch_ops.compute_threshold(master_inst_list=master_inst_list, ops_dict=curr_ops_dict)
    op_dict2, counts2 = branch_ops.group_by_branch_offset(master_inst_list=master_inst_list, ops_dict=curr_ops_dict, branch_threshold=branch_threshold)
    # print_stats(op_dict2, counts2)

    # Group by branch signs
    op_dict3, counts3 = branch_ops.group_by_branch_sign(master_inst_list=master_inst_list, ops_dict=curr_ops_dict)
    # print_stats(op_dict3, counts3)
    #ananlyses of cache
    cache.cache_simulator_example(master_inst_list, op_dict1['loads'], op_dict1['stores'])

    op_list, count4 = branch_ops.loop_compute(master_inst_list=master_inst_list, ops_dict=curr_ops_dict)

    op_list1, count5 = register_compute.register_compute(master_inst_list=master_inst_list)

    op_list5, count10 = register_compute.fregister_compute(master_inst_list=master_inst_list,extension_list=extension_list)

    op_dict4, count6 = jumps_ops.jumps_comput(master_inst_list=master_inst_list, ops_dict=curr_ops_dict)

    op_list2, count7 = jumps_ops.jump_size(master_inst_list=master_inst_list, ops_dict=curr_ops_dict)

    op_list3, count8 = dependency.raw_compute(master_inst_list=master_inst_list)

    op_list4, count9 = csr_compute.csr_compute(master_inst_list=master_inst_list, ops_dict=curr_ops_dict)

    op_list6, count11 = store_load_bypass.store_load_bypass(master_inst_list, op_dict1['loads'], op_dict1['stores'])
    if 'C' in extension_list:
        logger.warning("riscv-isac does not decode immediate fields for compressed instructions. \
Value based metrics on branch ops may be inaccurate.")

    utils.tabulate_stats(op_dict1, counts1, metric_name="Grouping Instructions by Type of Operation.")
    utils.tabulate_stats(op_dict, counts, metric_name="Grouping Instructions by Privilege Mode.")
    utils.tabulate_stats(op_dict2, counts2, metric_name="Grouping Branches by Offset Size.")
    utils.tabulate_stats(op_dict3, counts3, metric_name="Grouping Branches by Direction.")
    utils.tabulate_loop_stats(op_list, count4, metric_name="Nested loop Computation.")
    utils.tabulate_loop_stats(op_list1, count5, metric_name="Register Computation.")
    utils.tabulate_loop_stats(op_list5, count10, metric_name="Floating Point Register Computation.")
    utils.tabulate_stats(op_dict4, count6, metric_name="Jumps Computation.")
    utils.tabulate_loop_stats(op_list2, count7, metric_name="Jumps Size.")
    utils.tabulate_loop_stats(op_list3, count8, metric_name="Reads after Writes(RAW) Computation.")
    utils.tabulate_loop_stats(op_list4, count9, metric_name="CSR Computation.")
    utils.tabulate_loop_stats(op_list6, count11, metric_name="Store load bypass")