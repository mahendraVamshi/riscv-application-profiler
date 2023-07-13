from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts

def jumps_comput(master_inst_list: list ,ops_dict: dict):
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
    logger.info("computing jumps.")
    op_dict = {'forward': [], 'backward': []}
    for entry in master_inst_list:
        # issac doesnt give immidiate value for compressed instructions
        #logger.debug(print(entry))
        if entry.instr_name in ops_dict['jumps']:
            if str(entry.instr_name) == 'jalr':
                rs1 = str(entry.rs1[1]) + str(entry.rs1[0])
                jump_value = entry.imm + int(consts.reg_file[rs1],16)
            else:
                jump_value = entry.imm  
            if jump_value is None:
                logger.debug(entry)
                continue
            if jump_value<0:
                op_dict['backward'].append(entry)
            else:
                op_dict['forward'].append(entry)
    counts = {op: len(op_dict[op]) for op in op_dict.keys()}
    logger.debug('Done.')
    return (op_dict, counts)

def jump_size(master_inst_list: list, ops_dict: dict):
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
    logger.info("computing jump size.")
    # jumps={instr:{'direction': fo, 'size': value} for instr in ops_dict['jumps']}
    jump_instr={}
    jump_list=[]
    for entry in master_inst_list:
        if entry.instr_name in ops_dict['jumps']:
            if entry.imm is not None:
                instr=''
                ta=int(entry.instr_addr) + int(entry.imm)
                #issac doesnt give immidiate value for jalr
                if (entry.rd is not None):
                    instr=str(entry.instr_name)+' '+str(entry.rd[1])+str(entry.rd[0])+','
                if (entry.rs1 is not None):
                    if (instr==''):
                        instr=str(entry.instr_name)+' '+str(entry.rs1[1])+str(entry.rs1[0])+','
                    else:
                        instr=instr+' '+str(entry.rs1[1])+str(entry.rs1[0])+','
                if (entry.rs2 is not None):
                    if (instr==''):
                        instr=str(entry.instr_name)+' '+str(entry.rs2[1])+str(entry.rs2[0])+','
                    else:
                        instr=instr+' '+str(entry.rs2[1])+str(entry.rs2[0])+','
                if (entry.rs1 is None and entry.rs2 is None and entry.rd is None):
                    instr=str(entry.instr_name)
                instr=instr+' '+str(entry.imm)
                    
                if (instr not in jump_instr) or (hex(ta) not in jump_instr[instr]['target address']):
                    jump_instr[instr]={'target address':hex(ta),'count':1,'size(bytes)':abs(int(entry.instr_addr)-ta)}    
                else:
                    jump_instr[instr]['count']=jump_instr[instr]['count']+1
            else:
                if 'c.jr' in instr or 'c.jalr' in entry.instr_name:
                    rs1=str(entry.rs1[1])+str(entry.rs1[0])
                    ta=int(entry.instr_addr) + int(consts.reg_file[rs1],16)
                    jump_instr[entry.instr_name]={'target address':None,'count':1,'size(bytes)':None}
                logger.debug(print('immidiate value not found for :',entry))

    number_of_loops=len(jump_instr)
    if number_of_loops>1:
        jump_list=list(jump_instr.keys())
    return(jump_list,jump_instr)

                