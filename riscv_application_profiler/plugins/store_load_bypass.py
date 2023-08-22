from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts

def store_load_bypass (master_inst_list: list, ops_dict: dict):
    '''
    Computes the number of instances of store load bypass.
    
    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of
            InstructionEntry objects as values.
    
    Returns:
        - A list of addresses and a dictionary with the addresses as keys and the number of instances of store load bypass as values.
        
    '''

    # Log the start of the process for computing store-load bypass.
    logger.info("Computing store load bypass.")

    # Get the list of load and store operations.
    load_list = ops_dict['loads']
    store_list = ops_dict['stores']

    # Initialize a dictionary to store the resulting data.
    ret_dict = {'Address': [], 'Counts': []}

    # Initialize lists to store store and load addresses, and a dictionary for bypass information.
    store_address_list = []
    load_address_list = []
    bypass_dict = {}

    # Iterate through each instruction in master_inst_list.
    for i in master_inst_list:
        # Update register values based on commit information.
        if (i.reg_commit is not None):
            if (i.reg_commit[1] != '0'):
                consts.reg_file[f'x{i.reg_commit[1]}'] = i.reg_commit[2]

        # Check if the instruction is a load or a store operation.
        if (i in load_list or i in store_list):
            # Determine the base address for the memory access.
            if ('sp' in i.instr_name):
                base = int(consts.reg_file['x2'], 16)
                if (i.imm is None):
                    address = hex(base)
                else:
                    address = hex(base + i.imm)
            else:
                base = int(consts.reg_file[f'x{i.rs1[0]}'], 16)
                if (i.imm is None):
                    address = hex(base)
                else:
                    address = hex(base + i.imm)

            # Check if the instruction is a store operation.
            if (i in store_list):
                store_address_list.append(address)
            # Check if the instruction is a load operation.
            elif (i in load_list):
                if address in store_address_list:
                    if address in load_address_list:
                        bypass_dict[address]['counts'] += 1
                    else:
                        load_address_list.append(address)
                        bypass_dict[address] = {'counts': 0}

        # Update register values based on commit information.
        if (i.reg_commit is not None):
            if (i.reg_commit[1] != '0'):
                consts.reg_file[f'x{i.reg_commit[1]}'] = i.reg_commit[2]

    # Reset register values.
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}
    consts.reg_file['x2'] = '0x7ffffff0'
    consts.reg_file['x3'] = '0x100000'

    # Populate the result dictionary with store-load bypass information.
    for address in load_address_list:
        ret_dict['Address'].append(address)
        ret_dict['Counts'].append(bypass_dict[address]['counts'])

    # Log the completion of the store-load bypass computation.
    logger.debug('Done.')

    # Return the resulting dictionary containing store-load bypass data.
    return ret_dict


                
