from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts

def jumps_compute(master_inst_dict: dict ,ops_dict: dict, extension_used: list,config, cycle_accurate_config):
    '''
    Computes the number of jumps in the program.

    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of
        InstructionEntry objects as values.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.


    Returns:
        - A dictionary with the jumps as keys and the number of jumps which are forward and backward.
    '''
    # Log the start of the process for computing jumps.
    logger.info("Computing jumps.")

    # Initialize dictionaries to hold jump data and direction information.
    op_dict = {'forward': [], 'backward': []}
    direc_list = ['forward', 'backward']
    direc_dict = {'forward': {'count': 0}, 'backward': {'count': 0}}

    # Initialize a dictionary to hold the resulting direction and count data.
    ret_dict = {'Direction': direc_list, 'Count': []}

    # Iterate through each instruction in master_inst_dict.
    for entry in master_inst_dict:
        
        # Check if the instruction is a jump operation.
        if entry in ops_dict['jumps']:
            if str(entry.instr_name) == 'jalr':
                rs1 = str(entry.rs1[1]) + str(entry.rs1[0])
                rd = str(entry.rd[1]) + str(entry.rd[0])
                jump_value = entry.imm + int(consts.reg_file[rs1], 16)
                consts.reg_file[rd] = hex(int(entry.instr_addr) + 4)
            else:
                jump_value = entry.imm
            
            # Handle the case where jump_value is None or negative.
            if jump_value is None:
                if 'c.jr' in entry.instr_name or 'c.jalr' in entry.instr_name:
                    rs1 = str(entry.rs1[1]) + str(entry.rs1[0])
                    jump_value = int(entry.instr_addr) + int(consts.reg_file[rs1], 16)
                    if 'c.jalr' in entry.instr_name:
                        consts.reg_file['x1'] = hex(int(entry.instr_addr) + 2)
            if jump_value < 0:
                op_dict['backward'].append(entry)
                direc_dict['backward']['count'] += 1
            else:
                op_dict['forward'].append(entry)
                direc_dict['forward']['count'] += 1


        # Update register values based on commit information.
        if (entry.reg_commit is not None):
            name = str(entry.reg_commit[0]) + str(entry.reg_commit[1])
            if (name != 'x0'):
                consts.reg_file[name] = entry.reg_commit[2]

    # Reset register values.
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}
    
    # Log the completion of jump computation.
    logger.info('Done.')

    # Populate the result dictionary with direction and count information.
    ret_dict['Count'].append(direc_dict['forward']['count'])
    ret_dict['Count'].append(direc_dict['backward']['count'])

    # Return the resulting dictionary containing jump direction and count data.
    return ret_dict


def jump_size(master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
    '''
    Computes the number of jumps in the program.

    Args:
        - master_inst_dict: A dict of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of
        InstructionEntry objects as values.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.


    Returns:
        - A dictionary with the jumps as keys and the number of jumps and jump size.

    '''
    # Log the start of the process for computing jump size.
    logger.info("Computing jump size.")

    # Initialize dictionaries and lists to hold jump instruction data.
    jump_instr = {}     # Dictionary to store information about jump instructions.
    target_address = [] # List to store target addresses for jumps.
    ret_dict = {'Instruction name':[],'count':[],'size':[]} # Dictionary to store return data.

    # Iterate through each instruction in master_inst_dict.
    for entry in master_inst_dict:
        # Check if the instruction is a jump operation.
        if entry in ops_dict['jumps']:
            instr = ''  # Initialize instruction string.
            size = 0    # Initialize size of the jump.

            # Calculate the target address for the jump.
            if entry.imm is not None:
                if entry.instr_name == 'jalr':
                    rs1 = f"{entry.rs1[1]}{entry.rs1[0]}"
                    rd = f"{entry.rd[1]}{entry.rd[0]}"
                    ta = int(consts.reg_file[rs1], 16) + int(entry.imm)
                    instr = f"{entry.instr_name} {rd}, {entry.imm}({rs1})"
                    consts.reg_file[rd] = hex(int(entry.instr_addr) + 4)
                else:
                    jump_value = entry.imm
                    ta = int(entry.instr_addr) + int(jump_value)
                    if entry.instr_name == 'c.jal':
                        instr = f"{entry.instr_name} {entry.imm}"
                        consts.reg_file['x1'] = hex(int(entry.instr_addr) + 2)
                    elif entry.instr_name == 'c.j':
                        instr = f"{entry.instr_name} {entry.imm}"
                    elif entry.instr_name == 'jal':
                        rd = f"{entry.rd[1]}{entry.rd[0]}"
                        instr = f"{entry.instr_name} {rd}, {entry.imm}"
                        consts.reg_file['x1'] = hex(int(entry.instr_addr) + 4)
            elif entry.instr_name in {'c.jr', 'c.jalr'}:
                rs1 = f"{entry.rs1[1]}{entry.rs1[0]}"
                ta = int(consts.reg_file[rs1], 16)
                if 'c.jalr' in entry.instr_name:
                    consts.reg_file['x1'] = hex(int(entry.instr_addr) + 2)
                instr = f"{entry.instr_name} {rs1}"
            else:
                logger.debug(f"Immediate value not found for: {entry}")

            # Calculate the size of the jump instruction.
            size = abs(int(entry.instr_addr) - ta)

            # Update jump_instr dictionary with jump information.
            if instr not in jump_instr or (hex(ta) not in target_address and str(size) not in jump_instr[instr]['size(bytes)']):
                jump_instr[instr] = {'count': 1, 'size(bytes)': str(size)}
                target_address.append(hex(ta))
            else:
                jump_instr[instr]['count'] += 1

        # Update register values based on commit information.
        if entry.reg_commit is not None and entry.rd is not None:
            name = f"{entry.rd[1]}{entry.rd[0]}"
            if name != 'x0':
                consts.reg_file[name] = entry.reg_commit[2]

    # Reset register values.
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}
    # Populate the return dictionary with jump instruction data.   
    ret_dict['Instruction name'] = list(jump_instr.keys())
    ret_dict['count'] = [jump_instr[key]['count'] for key in jump_instr.keys()]
    ret_dict['size'] = [jump_instr[key]['size(bytes)'] for key in jump_instr.keys()]

    # Log the completion of jump size computation.
    logger.info('Done.')

    # Return the dictionary.
    return ret_dict



                