from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
from pprint import pprint

def store_load_bypass (master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
    '''
    Computes the number of instances of store load bypass.
    
    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of
            InstructionEntry objects as values.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.
    
    Returns:
        - A dictionary with the addresses, counts, depth and bypass width as keys and their values as values.
        
    '''

    # Log the start of the process for computing store-load bypass.
    logger.info("Computing store load bypass.")

    # make a bypass dict
    bypass_dict = {}
    tracking = {}
    eff_addr = []
    ret_dict = {'Address': [], 'Counts': [], 'Depth': [], 'Bypass Width': []}

    # iterate through master inst list
    # if a store is encountered, make a set of bytes touched and look out for loads from these bytes else continue
    # upon encountering a load that touches these bytes, freeze the depth and reset counts/depths

    for entry in master_inst_dict:
        if entry in ops_dict['stores']: # this is a store
            # Determine the base address for the memory access.
            reg_name = 'x2' if 'sp' in entry.instr_name else f'x{entry.rs1[0]}'
            base = int(consts.reg_file[reg_name], 16)
            address = hex(base + entry.imm) if entry.imm is not None else hex(base)
            access_sz = 8 if 'd' in entry.instr_name \
                        else 4 if 'w' in entry.instr_name \
                        else 2 if 'h' in entry.instr_name \
                        else 1 if 'b' in entry.instr_name \
                        else None
            
            # sanity check
            if access_sz is None:
                raise Exception(f'Invalid access size encountered: {entry.instr_name}')
            # make a set of all bytes touched by this store
            bytes_touched = {hex(int(address, 16) + i) for i in range(0, access_sz, 1)}
            for _entry in bytes_touched:
                tracking[_entry] = {}
                tracking[_entry]['depth'] = 0
                tracking[_entry]['s_access_sz'] = access_sz
        
        # look for loads
        if entry in ops_dict['loads']:
            # Determine the base address for the memory access.
            reg_name = 'x2' if 'sp' in entry.instr_name else f'x{entry.rs1[0]}'
            base = int(consts.reg_file[reg_name], 16)
            address = hex(base + entry.imm) if entry.imm is not None else hex(base)
            eff_addr.append(address)
            access_sz = 8 if 'd' in entry.instr_name \
                        else 4 if 'w' in entry.instr_name \
                        else 2 if 'h' in entry.instr_name \
                        else 1 if 'b' in entry.instr_name \
                        else None
            if access_sz is None:
                raise Exception(f'Invalid access size encountered: {entry.instr_name}')
            count = 0
            bytes_touched = {hex(int(address, 16) + i) for i in range(0, access_sz, 1)}
            for byte_entry in bytes_touched:
                if byte_entry in tracking:
                    count += 1
            for _entry in bytes_touched:
                if _entry in tracking:
                    if _entry in bypass_dict:
                        if bypass_dict[_entry]['depth'] == tracking[_entry]['depth']:
                            bypass_dict[_entry]['counts'] += 1
                        
                    else:
                        bypass_dict[_entry] = {'counts': 1, 'depth': tracking[_entry]['depth'], 'bypass_width': count}   
                    tracking.pop(_entry)
        
        if entry.instr_name not in ops_dict['loads']: # this is a regular instruction which causes a deeper bypass
            for _entry in tracking:
                tracking[_entry]['depth'] += 1

        # Update register values based on commit information.
        if (entry.reg_commit is not None):
            if (entry.reg_commit[1] != '0'):
                consts.reg_file[f'x{int(entry.reg_commit[1])}'] = entry.reg_commit[2]

    keys_to_remove = []

    # Iterate over the dictionary and identify keys to remove.
    for entry in bypass_dict:
        if entry not in eff_addr:
            keys_to_remove.append(entry)

    # Remove the identified keys from the dictionary.
    for key in keys_to_remove:
        bypass_dict.pop(key)

        


    # Reset register values.
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}

    # Populate the result dictionary with store-load bypass information.
    for address in bypass_dict:
        ret_dict['Address'].append(address)
        ret_dict['Counts'].append(bypass_dict[address]['counts'])
        ret_dict['Depth'].append(bypass_dict[address]['depth'])
        ret_dict['Bypass Width'].append(bypass_dict[address]['bypass_width'])

    # Log the completion of the store-load bypass computation.
    logger.info('Done.')

    # Return the resulting dictionary containing store-load bypass data.
    return ret_dict


                