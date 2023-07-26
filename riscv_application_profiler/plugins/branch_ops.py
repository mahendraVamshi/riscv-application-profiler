# See LICENSE for licensing information.

# this file is a plugin for riscv_application_profiler
# this file classifies instructions into groups based on +ve/-ve branch offsets.
# this file classifies instructions into 'long' and 'short' branches based on branch offsets.

from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import statistics
import pprint as pp

def compute_threshold(master_inst_list: list, ops_dict: dict) -> int:
    '''
    compute the mean plus two standard deviations as the threshold
    
    Args:
        - master_inst_list: A list of InstructionEntry objects.
    '''

    # compute the list of branch offsets from the master_inst_list where each entry has an imm field
    branch_offsets = [entry.imm for entry in master_inst_list if entry in ops_dict['branches'] and entry.imm is not None]

    # compute the mean and standard deviation of the branch offsets
    mean = statistics.mean(branch_offsets)
    std_dev = statistics.stdev(branch_offsets)

    # compute the threshold as the mean plus two standard deviations
    threshold = mean + 2*std_dev

    return int(threshold)

def group_by_branch_offset(master_inst_list: list, ops_dict: dict, branch_threshold: int = 0):
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
    size_list = ['long', 'short']
    size_dict = {'long': {'count':0}, 'short': {'count':0}}
    
    for entry in master_inst_list:
        if entry in ops_dict['branches']:
            if entry.imm is None:
                continue
            if entry.imm < branch_threshold:
                # op_dict['short'].append(entry)
                size_dict['short']['count'] += 1
            else:
                # op_dict['long'].append(entry)
                size_dict['long']['count'] += 1
    
    logger.debug('Done.')
    return (size_list, size_dict)

def group_by_branch_sign(master_inst_list: list, ops_dict: dict):
    '''
    Groups instructions based on the sign bit of the branch offset.
    
    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - ops_dict: A dictionary with the operations as keys and a list of InstructionEntry
    
    Returns:
        -A list of directions, which in this case are 'positive' and 'negative'.
        A dictionary direc_dict containing the counts of instructions in each direction. 
        The keys are 'positive' and 'negative', and the values are dictionaries containing the 
        'count' of instructions with positive and negative branch offsets.

    '''
    logger.info("Grouping instructions by branch offset sign.")
    # Create a dictionary with the operations as keys
    op_dict = {'positive': [], 'negative': []}
    direc_list = ['positive', 'negative']
    direc_dict = {'positive': {'count':0}, 'negative': {'count':0}}

    for entry in master_inst_list:
        if entry in ops_dict['branches']:
            if entry.imm is None:
                continue
            if entry.imm<0:
                direc_dict['negative']['count'] += 1
                # op_dict['negative'].append(entry)
            else:
                direc_dict['positive']['count'] += 1
                # op_dict['positive'].append(entry)
    logger.debug('Done.')
    return (direc_list, direc_dict)


def loop_compute(master_inst_list: list, ops_dict: dict):
    '''
    Groups instructions based on the branch offset.
    
    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - ops_dict: A dictionary with the operations as keys and a list of InstructionEntry
        
    Returns:
        - A list of loops, which in this case are loops with a single branch instruction.
        A dictionary loop_instr containing the counts of instructions in each loop.
        The keys are the branch instructions, and the values are dictionaries containing the
        'target address', 'depth', 'count' and 'size' of the loop.
            '''
    logger.info("Computing loops.")
    # Create a dictionary with the operations as keys
    loop_instr={}
    target_address={}
    loop_list=[]
    for entry in master_inst_list:
        if entry in ops_dict['branches']:
            if entry.imm is None:
                continue
            if entry.imm<0:
                if entry.rs2 is not None:
                    instr=str(entry.instr_name)+' '+str(entry.rs1[1])+str(entry.rs1[0])+','+str(entry.rs2[1])+str(entry.rs2[0])
                else:
                    instr=str(entry.instr_name)+' '+str(entry.rs1[1])+str(entry.rs1[0])
                # loop_instr=>{ first_instr: {'target address':value,'depth':value,'count':value,'size':value}, second_instr: {'target address':value,'depth':value,'count':value,'size':value} }
                ta=int(entry.instr_addr) + int(entry.imm)
                if (instr not in loop_instr) or (hex(ta) not in target_address[instr]):

                    loop_instr[instr]={'depth':1,'count':1,'size(bytes)':(int(entry.instr_addr)-ta)}
                    target_address[instr]=hex(ta)
                    
                else:
                    loop_instr[instr]['count']=loop_instr[instr]['count']+1
    
    number_of_loops=len(loop_instr)
    if number_of_loops>1:
        loop_list=list(loop_instr.keys())
        for i in range(number_of_loops-1):
            if (loop_list[i+1]<loop_list[i]):
                loop_instr[loop_list[i+1]]['depth']=loop_instr[loop_list[i]]['depth']+1

    return(loop_list,loop_instr)
    