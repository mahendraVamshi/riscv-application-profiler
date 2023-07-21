from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import statistics

def raw_compute(master_inst_list: list):
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
    logger.info("Computing register reads after writes.")
    reg_list=list(consts.reg_file.keys())
    regs = {i : {'depth': 1} for i in reg_list}
    raw={}
    instruction_list=[]
    depth=[]
    raw_list = []
    prev_names = []  # Variable to store the previous entry.rd value

    for entry in master_inst_list:
        if (entry.rs1 is not None):
            name = str(entry.rs1[1]) + str(entry.rs1[0])
            instr = str(entry.instr_name)
            if name in prev_names:
                instruction=prev_instr+'  '+instr
                if instruction in raw:# and name in raw[instruction]['reg'] and regs[name]['depth']==raw[instruction]['depth']:
                    if regs[name]['depth']==raw[instruction]['depth']:
                        raw[instruction]['count'] += 1
                        prev_names.remove(name)
                        regs[name]['depth'] = 1
                else:
                    raw[instruction]= {'depth':regs[name]['depth'], 'count':1}
                    instruction_list.append(instruction)
                    prev_names.remove(name)
                    regs[name]['depth'] = 1
            else:
                regs[name]['depth'] += 1   

        if (entry.rs2 is not None):
            name = str(entry.rs2[1]) + str(entry.rs2[0])
            instr = str(entry.instr_name)
            if name in prev_names:
                instruction=prev_instr+'  '+instr
                if instruction in raw: #and name in raw[instruction]['reg'] and regs[name]['depth']==raw[instruction]['depth']:
                    if regs[name]['depth']==raw[instruction]['depth']:
                        raw[instruction]['count'] += 1
                        prev_names.remove(name)
                        regs[name]['depth'] = 1
                else:
                    raw[instruction]= {'depth':regs[name]['depth'], 'count':1}
                    instruction_list.append(instruction)
                    prev_names.remove(name)
                    regs[name]['depth'] = 1
            else:
                regs[name]['depth'] += 1 
            
        if (entry.rd is not None):
            name = str(entry.rd[1]) + str(entry.rd[0])
            prev_instr = str(entry.instr_name)
            if name not in prev_names:
                prev_names.append(name)
            else:
                regs[name]['depth'] = 1
    
    

    return instruction_list, raw