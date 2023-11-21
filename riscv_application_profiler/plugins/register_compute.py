from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import statistics

def register_compute(master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
    '''
    Computes the number of reads and writes to each register.
    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of InstructionEntry objects as values.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.


    Returns:
        - A dictionary with the registers as keys and a list of reads and writes as values.
    '''
    # Log the start of the process for computing register read and write counts.
    logger.info("Computing register read writes.")

    # Get a list of all registers in the register file.
    reg_list = list(consts.reg_file.keys())

    # Initialize a dictionary to track read and write counts for each register.
    regs = {i: {'write_count': 0, 'read_count': 0} for i in reg_list}

    # Initialize dictionaries to hold the resulting data.
    ret_dict = {'Register': [], 'Reads': [], 'Writes': []}

    # Iterate through the list of instructions in master_inst_dict.
    for entry in master_inst_dict:
        # Check if the instruction uses rs1 register.
        if entry.rs1 is not None:
            name = str(entry.rs1[1]) + str(entry.rs1[0])
            regs[name]['read_count'] += 1
        # Check if the instruction uses rs2 register.
        if entry.rs2 is not None:
            name = str(entry.rs2[1]) + str(entry.rs2[0])
            regs[name]['read_count'] += 1
        # Check if the instruction defines a destination register (rd).
        if entry.rd is not None:
            name = str(entry.rd[1]) + str(entry.rd[0])
            regs[name]['write_count'] += 1
            # if (entry.reg_commit is None):
            #     if 'fence' in entry.instr_name or 'j' in entry.instr_name:
            #         continue
            #     # print(entry)
            # else:
            #     if 'l' in entry.instr_name or 's' in entry.instr_name:
            #         continue
            #     print(entry)

    # Populate the result dictionary with register read and write counts.
    for reg in reg_list:
        ret_dict['Register'].append(reg)
        ret_dict['Reads'].append(regs[reg]['read_count'])
        ret_dict['Writes'].append(regs[reg]['write_count'])

    logger.info('Done.')

    # Return the resulting dictionary containing register read and write counts.
    return ret_dict


def fregister_compute(master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
    '''
    Computes the number of reads and writes to each floating point register.
    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of InstructionEntry objects as values.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.


    Returns:
        - A dictionary with the registers as keys and a list of reads and writes as values.
        '''
    # Log the start of the process for computing F_register read and write counts.
    logger.info("Computing F_register read writes.")

    # Initialize an empty list to store F_register names and a dictionary to track counts.
    reg_list = []
    regs = {}

    # Initialize dictionaries to hold the resulting data.
    ret_dict = {'F_Register': [], 'Reads': [], 'Writes': []}

    # Check if 'F' and 'D' extensions are present, if not, return empty lists and dictionary.
    if 'F' not in extension_used or 'D' not in extension_used:
        return (ret_dict)

    # Log that the process of computing register read and write counts is starting.
    logger.info("Computing register read writes.")

    # Get a list of all F_registers in the F_register file.
    reg_list = list(consts.freg_file.keys())

    # Initialize a dictionary to track read and write counts for each F_register.
    regs = {i: {'write_count': 0, 'read_count': 0} for i in reg_list}

    # Initialize dictionaries to hold the resulting data.
    ret_dict = {'F_Register': [], 'Reads': [], 'Writes': []}

    # Iterate through the list of instructions in master_inst_dict.
    for entry in master_inst_dict:
        inst_name = str(entry.instr_name)
        # Check if the instruction involves F_registers.
        if 'f' in inst_name:
            # Check if the instruction uses rs1 F_register.
            if entry.rs1 is not None and 'x' not in entry.rs1[1]:
                name = str(entry.rs1[1]) + str(entry.rs1[0])
                regs[name]['read_count'] += 1
            # Check if the instruction uses rs2 F_register.
            if entry.rs2 is not None and 'x' not in entry.rs2[1]:
                name = str(entry.rs2[1]) + str(entry.rs2[0])
                regs[name]['read_count'] += 1
            # Check if the instruction defines a destination F_register (rd).
            if entry.rd is not None and 'x' not in entry.rd[1]:
                name = str(entry.rd[1]) + str(entry.rd[0])
                regs[name]['write_count'] += 1

    # Populate the result dictionary with F_register read and write counts.
    for reg in reg_list:
        ret_dict['F_Register'].append(reg)
        ret_dict['Reads'].append(regs[reg]['read_count'])
        ret_dict['Writes'].append(regs[reg]['write_count'])

    # Log the completion of F_register read and write computation.
    logger.info('Done.')

    # Return the resulting dictionary containing F_register read and write counts.
    return ret_dict