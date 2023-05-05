# See LICENSE for licensing information.

# this file is a plugin for riscv_application_profiler
# this file classifies instructions into groups based on +ve/-ve branch offsets.
# this file classifies instructions into 'long' and 'short' branches based on branch offsets.

from riscv_isac.log import *
from riscv_application_profiler.consts import *
import statistics

def compute_threshold(master_inst_list: list) -> int:
    '''
    compute the mean plus two standard deviations as the threshold
    
    Args:
        - master_inst_list: A list of InstructionEntry objects.
    '''

    # compute the list of branch offsets from the master_inst_list where each entry has an imm field
    branch_offsets = [entry.imm for entry in master_inst_list if entry.instr_name in ops_dict['branches']]

    # compute the mean and standard deviation of the branch offsets
    mean = statistics.mean(branch_offsets)
    std_dev = statistics.stdev(branch_offsets)

    # compute the threshold as the mean plus two standard deviations
    threshold = mean + 2*std_dev

    return int(threshold)

def group_by_branch_offset(master_inst_list: list, branch_threshold: int = 0):
    '''
    Groups instructions based on the branch offset.

    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - branch_threshold: The threshold for a branch to be considered 'long'.

    Returns:
        - A tuple containing a dictionary with the operations as keys and a list of
            InstructionEntry objects as values, and a dictionary with the operations as
            keys and the number of instructions in each group as values.
    '''
    logger.info("Grouping instructions by branch offset.")
    # Create a dictionary with the operations as keys
    op_dict = {'long': [], 'short': []}
    
    for entry in master_inst_list:
        if entry.instr_name in ops_dict['branches']:
            if entry.imm < branch_threshold:
                op_dict['short'].append(entry)
            else:
                op_dict['long'].append(entry)
    
    counts = {op: len(op_dict[op]) for op in op_dict.keys()}
    logger.debug('Done.')
    return (op_dict, counts)

def group_by_branch_sign(master_inst_list: list):
    '''
    Groups instructions based on the sign bit of the branch offset.
    
    Args:
        - master_inst_list: A list of InstructionEntry objects.
    
    Returns:
        - A tuple containing a dictionary with the operations as keys and a list of
            InstructionEntry objects as values, and a dictionary with the operations as
            keys and the number of instructions in each group as values.
    '''
    logger.info("Grouping instructions by branch offset sign.")
    # Create a dictionary with the operations as keys
    op_dict = {'positive': [], 'negative': []}
    for entry in master_inst_list:
        if entry.instr_name in ops_dict['branches']:
            if entry.imm<0:
                op_dict['negative'].append(entry)
            else:
                op_dict['positive'].append(entry)
    
        
 
    counts = {op: len(op_dict[op]) for op in op_dict.keys()}
    logger.debug('Done.')
    return (op_dict, counts)