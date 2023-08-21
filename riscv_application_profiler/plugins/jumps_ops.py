from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts

def jumps_comput(master_inst_list: list ,ops_dict: dict):
    '''
    Computes the number of jumps in the program.

    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of

    Returns:
        - A list of directions and a dictionary with the directions as keys and the number of jumps
    '''
    logger.info("computing jumps.")
    op_dict = {'forward': [], 'backward': []}
    direc_list = ['forward', 'backward']
    direc_dict = {'forward': {'count':0}, 'backward': {'count':0}}
    ret_dict = {'Direction': direc_list, 'Count': []}
    for entry in master_inst_list:

        if (entry.reg_commit is not None):
            name = str(entry.reg_commit[0]) + str(entry.reg_commit[1])
            if (name != 'x0'):
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
    ret_dict['Count'].append(direc_dict['forward']['count'])
    ret_dict['Count'].append(direc_dict['backward']['count'])
    return (ret_dict)

def jump_size(master_inst_list: list, ops_dict: dict):
    '''
    Computes the number of jumps in the program.

    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of

    Returns:
        - A list of jumps and a dictionary with the jumps as keys and the number of jumps and jump size.

    '''
    logger.info("computing jump size.")
    # jumps={instr:{'direction': fo, 'size': value} for instr in ops_dict['jumps']}
    jump_instr = {}
    jump_list = []
    target_address = {}

    for entry in master_inst_list:
        if entry in ops_dict['jumps']:
            instr = ''
            if entry.imm is not None:
                if entry.instr_name == 'jalr':
                    rs1 = f"{entry.rs1[1]}{entry.rs1[0]}"
                    rd = f"{entry.rd[1]}{entry.rd[0]}"
                    ta = int(consts.reg_file[rs1], 16)
                    consts.reg_file[rd] = hex(int(entry.instr_addr) + 4)
                else:
                    jump_value = entry.imm
                    ta = int(entry.instr_addr) + int(jump_value)
                    if entry.instr_name == 'c.jal':
                        consts.reg_file['x1'] = hex(int(entry.instr_addr) + 2)
                    elif entry.instr_name == 'jal':
                        consts.reg_file['x1'] = hex(int(entry.instr_addr) + 4)
                    
                instr_parts = []
                if entry.rd is not None:
                    instr_parts.append(f"{entry.rd[1]}{entry.rd[0]}")
                if entry.rs1 is not None:
                    instr_parts.append(f"{entry.rs1[1]}{entry.rs1[0]}")
                if entry.rs2 is not None:
                    instr_parts.append(f"{entry.rs2[1]}{entry.rs2[0]}")
                if not instr_parts:
                    instr = entry.instr_name
                else:
                    instr = f"{entry.instr_name} {' '.join(instr_parts)}"
                instr += f" {entry.imm}"
                
                if instr not in jump_instr or hex(ta) not in target_address.get(instr, []):
                    jump_instr[instr] = {'count': 1, 'size(bytes)': abs(int(entry.instr_addr) - ta)}
                    target_address.setdefault(instr, []).append(hex(ta))
                else:
                    jump_instr[instr]['count'] += 1
            
            elif entry.instr_name in {'c.jr', 'c.jalr'}:
                rs1 = f"{entry.rs1[1]}{entry.rs1[0]}"
                ta = int(consts.reg_file[rs1], 16)

                if 'c.jalr' in entry.instr_name:
                    consts.reg_file['x1'] = hex(int(entry.instr_addr) + 2)
                
                size = abs(int(entry.instr_addr) - ta)
                instr = f"{entry.instr_name} {rs1}"
                if instr not in jump_instr or (hex(ta) not in jump_instr[instr]['target address'] and str(size) not in jump_instr[instr]['size(bytes)']):
                    jump_instr[instr] = {'target address': hex(ta), 'count': 1, 'size(bytes)': str(size)}
                else:
                    jump_instr[instr]['count'] += 1
            
            else:
                logger.debug(f"Immediate value not found for: {entry}")
            
        if entry.reg_commit is not None and entry.rd is not None:
            name = f"{entry.rd[1]}{entry.rd[0]}"
            if name != 'x0':
                consts.reg_file[name] = entry.reg_commit[2]

    number_of_loops = len(jump_instr)
    if number_of_loops > 1:
        jump_list = list(jump_instr.keys())

    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}
    consts.reg_file['x2'] = '0x7ffffff0'
    consts.reg_file['x3'] = '0x100000'

    return jump_list, jump_instr


                