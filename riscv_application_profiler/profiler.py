import re
from riscv_application_profiler.consts import *
import pprint as prettyprint
import math
from riscv_isac.log import *
from riscv_isac.plugins.spike import *
from riscv_application_profiler.plugins import instr_groups
from riscv_application_profiler.plugins import branch_ops
import riscv_config.isa_validator as isaval

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
    from build.rvopcodesdecoder import disassembler
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
    ]

    (extension_list, err, err_list) = isaval.get_extension_list(isa)
    #print (extension_list)
    for e in err_list:
        logger.error(e)
    if err:
        raise SystemExit(1)
    
    ISA = isa.split('I')[0]

   # groups = list(ops_dict.keys())

    op_dict1, counts1 = instr_groups.group_by_operation(groups, ISA, extension_list, master_inst_list)
    print_stats(op_dict1, counts1)

    # Group by branch sizes
    branch_threshold = 0
    op_dict2, counts2 = branch_ops.group_by_branch_offset(master_inst_list, branch_threshold)

    # Group by branch signs
    op_dict3, counts3 = branch_ops.group_by_branch_sign(master_inst_list)