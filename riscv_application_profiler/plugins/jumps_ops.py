from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import os
import yaml

script_directory = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '..', 'config.yaml')
with open(config_path, 'r') as config_file:
    config = yaml.safe_load(config_file)

def jumps_comput(master_inst_list: list ,ops_dict: dict):
    '''
    Computes the number of jumps in the program.

    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of

    Returns:
        - A list of directions and a dictionary with the directions as keys and the number of jumps
    '''
    if 'cfg1' in config['profiles']:
        metrics = config['profiles']['cfg1']['metrics']
        if 'jumps_ops' in metrics:
            logger.info("Computing jumps.")
    
    op_dict = {'forward': [], 'backward': []}
    direc_list = ['forward', 'backward']
    direc_dict = {'forward': {'count':0}, 'backward': {'count':0}}
    for entry in master_inst_list:

        if (entry.reg_commit is not None):
            name = str(entry.reg_commit[0]) + str(entry.reg_commit[1])
            consts.reg_file[name] = entry.reg_commit[2]
        if entry in ops_dict['jumps']:
            if str(entry.instr_name) == 'jalr':
                rs1 = str(entry.rs1[1]) + str(entry.rs1[0])
                rd = str(entry.rd[1]) + str(entry.rd[0])
                jump_value = entry.imm + int(consts.reg_file[rs1],16)
                consts.reg_file[rd]=hex(int(entry.instr_addr)+4)
            else:
                jump_value = entry.imm  
            if jump_value is None:
                if 'c.jr' in entry.instr_name or 'c.jalr' in entry.instr_name:
                    rs1=str(entry.rs1[1])+str(entry.rs1[0])
                    jump_value=int(entry.instr_addr) + int(consts.reg_file[rs1],16)
                    if 'c.jalr' in entry.instr_name:
                        consts.reg_file['x1']=hex(int(entry.instr_addr)+2)
            if jump_value<0:
                op_dict['backward'].append(entry)
                direc_dict['backward']['count'] += 1
            else:
                op_dict['forward'].append(entry)
                direc_dict['forward']['count'] += 1
    logger.debug('Done.')
    return (direc_list, direc_dict)

def jump_size(master_inst_list: list, ops_dict: dict):
    '''
    Computes the number of jumps in the program.

    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of

    Returns:
        - A list of jumps and a dictionary with the jumps as keys and the number of jumps and jump size.

    '''
    if 'cfg1' in config['profiles']:
        metrics = config['profiles']['cfg1']['metrics']
        if 'jumps_ops' in metrics:
            logger.info("computing jump size.")
    
    # jumps={instr:{'direction': fo, 'size': value} for instr in ops_dict['jumps']}
    jump_instr={}
    jump_list=[]
    target_address={}
    for entry in master_inst_list: 
        
        if entry in ops_dict['jumps']:
            instr=''
            if entry.imm is not None:
                if str(entry.instr_name) == 'jalr':
                    rs1 = str(entry.rs1[1]) + str(entry.rs1[0])
                    rd = str(entry.rd[1]) + str(entry.rd[0])
                    jump_value = int(consts.reg_file[rs1],16)
                    consts.reg_file[rd]=hex(int(entry.instr_addr)+4)
                else:
                    jump_value = entry.imm 
                ta=int(entry.instr_addr) + int(jump_value)

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
                    
                if (instr not in jump_instr) or (hex(ta) not in target_address[instr]):
                    jump_instr[instr]={'count':1,'size(bytes)':abs(int(entry.instr_addr)-ta)}
                    target_address[instr]=[hex(ta)]    
                else:
                    jump_instr[instr]['count']=jump_instr[instr]['count']+1
            elif (entry.instr_name=='c.jr') or (entry.instr_name=='c.jalr'):
                rs1=str(entry.rs1[1])+str(entry.rs1[0])
                ta=int(entry.instr_addr) + int(consts.reg_file[rs1],16)

                if 'c.jalr' in entry.instr_name:
                    consts.reg_file['x1']=hex(int(entry.instr_addr)+2)
                size=abs(int(entry.instr_addr)-ta)
                instr=str(entry.instr_name)+' '+str(entry.rs1[1])+str(entry.rs1[0])
                if (instr not in jump_instr) or ((hex(ta) not in jump_instr[instr]['target address']) and (str(size) not in jump_instr[instr]['size(bytes)'])):
                    jump_instr[instr]={'target address':hex(ta),'count':1,'size(bytes)':str(size)}
                else:
                    jump_instr[instr]['count']=jump_instr[instr]['count']+1
            else:
                logger.debug(print('immidiate value not found for :',entry))
        

        if (entry.reg_commit is not None):
            name = str(entry.reg_commit[0]) + str(entry.reg_commit[1])
            if (int(entry.reg_commit[2],16)>0):
                consts.reg_file[name] = entry.reg_commit[2]

    number_of_loops=len(jump_instr)
    if number_of_loops>1:
        jump_list=list(jump_instr.keys())
    return(jump_list,jump_instr)

                