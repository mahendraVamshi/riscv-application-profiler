# See LICENSE for licensing information.

# this file is a plugin for riscv_application_profiler
# this file classifies instructions into groups based on +ve/-ve branch offsets.
# this file classifies instructions into 'long' and 'short' branches based on branch offsets.

from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import statistics
import pprint as pp

def compute_threshold(master_inst_dict: dict, ops_dict: dict) -> int:
    '''
    compute the mean plus two standard deviations as the threshold
    
    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of InstructionEntry objects as values.
    '''

    # compute the list of branch offsets from the master_inst_dict where each entry has an imm field
    branch_offsets = [entry.imm for entry in ops_dict['branches'] if entry.imm is not None]

    # compute the mean and standard deviation of the branch offsets
    if len(branch_offsets) == 0:
        return 0
    mean = statistics.mean(branch_offsets)
    std_dev = statistics.stdev(branch_offsets)

    # compute the threshold as the mean plus two standard deviations
    threshold = mean + 2*std_dev

    return int(threshold)

def group_by_branch_offset(master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
    '''
    Groups instructions based on the branch offset.

    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - branch_threshold: The threshold for a branch to be considered 'long'.
        - ops_dict: A dictionary containing the operations as keys and a list of InstructionEntry objects as values.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.

    Returns:
        - A dictionary with the branch offset sizes and count as keys and values respectively. 
    '''
    # Logging the grouping process
    logger.info("Grouping instructions by branch offset.")

    branch_threshold = compute_threshold(master_inst_dict, ops_dict)

    # Initializing dictionaries and lists
    size_list = ['long', 'short']
    size_dict = {size: {'count': 0} for size in size_list}
    ret_dict = {'Offset Size': size_list, 'Count': []}

    # loop though the branch instructions
    for entry in ops_dict['branches']:
        if entry.imm is None:
            continue
        # Determine whether the branch is long or short based on the threshold
        size = 'short' if entry.imm < branch_threshold else 'long'
        size_dict[size]['count'] += 1

    # Logging completion of the grouping process
    logger.info('Done.')

    # Appending the counts to the result dictionary
    ret_dict['Count'].append(size_dict['long']['count'])
    ret_dict['Count'].append(size_dict['short']['count'])

    # Return the final results
    return ret_dict


def group_by_branch_sign(master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
    '''
    Groups instructions based on the sign bit of the branch offset.
    
    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - ops_dict: A dictionary with the operations as keys and a list of InstructionEntry.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.

    
    Returns:
        -A list of directions, which in this case are 'positive' and 'negative'.
        A dictionary direc_dict containing the counts of instructions in each direction. 
        The keys are 'positive' and 'negative', and the values are dictionaries containing the 
        'count' of instructions with positive and negative branch offsets.

    '''
    # Logging the grouping process
    logger.info("Grouping instructions by branch offset sign.")

    # Initializing dictionaries and lists
    direc_list = ['positive', 'negative']
    direc_dict = {direc: {'count': 0} for direc in direc_list}
    ret_dict = {'Direction': direc_list, 'Count': []}

    # Loop through branch instructions 
    for entry in ops_dict['branches']:
        if entry.imm is None:
            continue
        # Determine whether the branch offset is positive or negative
        direction = 'positive' if entry.imm >= 0 else 'negative'
        direc_dict[direction]['count'] += 1

    # Logging completion of the grouping process
    logger.info('Done.')

    # Appending the counts to the result dictionary
    ret_dict['Count'].append(direc_dict['positive']['count'])
    ret_dict['Count'].append(direc_dict['negative']['count'])

    # Return the final results
    return ret_dict



def loop_compute (master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
    '''
    Groups instructions based on the branch offset.
    
    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - ops_dict: A dictionary with the operations as keys and a list of InstructionEntry.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.
        
    Returns:
        - A dictionary loop_instr containing the counts of instructions in each loop.
        The keys are the branch instructions, and the values are dictionaries containing the
        'target address', 'depth', 'count' and 'size' of the loop.
            '''
    # Logging the loop computation process
    logger.info("Computing loops.")

    # Initializing dictionaries, lists, and result dictionary
    loop_instr = {}
    target_address = {}
    loop_list = []
    ret_dict = {'Branch Instruction': loop_list, 'Depth': [], 'Count': [], 'Size(bytes)': []}

    # Loop through branch instructions
    for entry in ops_dict['branches']:
        if entry.imm is None:
            continue
        # Determine the instruction and its target address
        if entry.rs2 is not None:
            instr = f"{entry.instr_name} {entry.rs1[1]}{entry.rs1[0]},{entry.rs2[1]}{entry.rs2[0]}"
        else:
            instr = f"{entry.instr_name} {entry.rs1[1]}{entry.rs1[0]}"
        ta = int(entry.instr_addr) + int(entry.imm)
        
        # Update loop information in the dictionaries
        if instr not in loop_instr or hex(ta) not in target_address.get(instr, []):
            loop_instr[instr] = {'depth': 1, 'count': 1, 'size(bytes)': abs(int(entry.instr_addr) - ta)}
            target_address.setdefault(instr, []).append(hex(ta))
        else:
            loop_instr[instr]['count'] = loop_instr[instr]['count'] + 1

    # Calculate the number of loops
    number_of_loops = len(loop_instr)

    # Initialize loop_list based on conditions
    loop_list = list(loop_instr.keys())
    for i in range(number_of_loops - 1):
        if loop_list[i + 1] < loop_list[i]:
            loop_instr[loop_list[i + 1]]['depth'] = loop_instr[loop_list[i]]['depth'] + 1

    # Populate the ret_dict with loop information
    for i in range(number_of_loops):
        ret_dict['Branch Instruction'].append(loop_list[i])
        ret_dict['Depth'].append(loop_instr[loop_list[i]]['depth'])
        ret_dict['Count'].append(loop_instr[loop_list[i]]['count'])
        ret_dict['Size(bytes)'].append(loop_instr[loop_list[i]]['size(bytes)'])

    # Logging completion of the loop computation process
    logger.info('Done.')

    # Return the final results
    return ret_dict

    