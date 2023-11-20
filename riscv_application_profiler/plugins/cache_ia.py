from cachesim import CacheSimulator, Cache, MainMemory
import riscv_application_profiler.consts as consts
from riscv_isac.log import *

def data_cache_simulator(master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
    '''
    Cache simulator for data cache.
    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - op_dict: A dictionary with the operations as keys and a list of
            InstructionEntry objects as values.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.
        
        Returns:
            - A dictionary with the cache level as keys and a list of cache utilization information as values.
        '''
    # Logging cache statistics
    logger.info("Data Cache Statistics:")

    # List of cache levels
    cache_list = ['Level 1']

    # Dictionary to store cache utilization information
    cache_dict = {l: {'max utilization(%)': 0, "avg utilization": 0} for l in cache_list}

    # Dictionary to store the final results
    ret_dict = {'Data Cache': ['Level 1'], 'Data cache Maximum Utilization(%)': [], 'Data cache Average Utilization': []}

    # Setting up memory and cache parameters
    no_of_sets = config['profiles']['cfg']['data_cache']['no_of_sets']
    no_of_ways = config['profiles']['cfg']['data_cache']['no_of_ways']
    line_size = config['profiles']['cfg']['data_cache']['line_size']
    replacement_policy = config['profiles']['cfg']['data_cache']['replacement_policy']
    total_cache_line = no_of_sets * no_of_ways
    number_of_words_in_line = line_size//4 # line size in byptes / 4 bytes (word size)

    data_util_list = []
    total_util = 0

    # Creating the L1 cache
    mem = MainMemory()
    l1 = Cache("L1", no_of_sets, no_of_ways, line_size, replacement_policy)
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)
    # Initializing minimum and maximum utilization


    # Initializing minimum and maximum utilization
    min_util = max_util = cs.count_invalid_entries('L1')

    # Loop through instructions
    for entry in master_inst_dict:

        if 'fence' in entry.instr_name:
            max_util *= line_size
            min_util *= line_size
            temp_total_util = ((max_util - min_util) / max_util) * 100
            data_util_list.append(temp_total_util)
            if temp_total_util > total_util:
                total_util = temp_total_util
            cs.force_write_back("L1")
            cs.mark_all_invalid("L1")
            min_util = max_util = cs.count_invalid_entries("L1")
        
        # Handle load/store instructions
        if entry in ops_dict['loads'] or entry in ops_dict['stores']:
            # Determine the address based on instruction type
            if 'sp' in entry.instr_name:
                base = int(consts.reg_file['x2'], 16)
            else:
                rs = str(entry.rs1[1]) + str(entry.rs1[0])
                base = int(consts.reg_file.get(rs, consts.freg_file.get(rs, '0x0')), 16)
            if entry.imm is None:
                address = base
            else:
                address = base + entry.imm
            
            # Determine the byte length for the operation
            if ('d' in entry.instr_name):
                byte_length = 8
            elif ('w' in entry.instr_name):
                byte_length = 4
            elif ('h' in entry.instr_name):
                byte_length = 2
            elif ('b' in entry.instr_name):
                byte_length = 1
            
            # Handle load and store operations
            if entry in ops_dict['loads']:
                cs.load(address, byte_length)
            elif entry in ops_dict['stores']:
                cs.store(address, byte_length)

            # Update current utilization and track min/max values
            this_util = cs.count_invalid_entries('L1')
            max_util = max(max_util, this_util)
            min_util = min(min_util, this_util)

        
        # Handle register commits
        if entry.reg_commit and entry.reg_commit[1] != '0':
            consts.reg_file[f'x{int(entry.reg_commit[1])}'] = entry.reg_commit[2]

    # Print cache statistics
    cs.print_stats()

    # Calculate total utilization percentages
    max_util *= line_size
    min_util *= line_size
    temp_total_util = ((max_util - min_util) / max_util) * 100
    data_util_list.append(temp_total_util)
    if temp_total_util > total_util:
        total_util = temp_total_util

    # Update cache utilization information
    cache_dict['Level 1']['max utilization(%)'] = total_util
    cache_dict['Level 1']['avg utilization'] = sum(data_util_list)/len(data_util_list)
    ret_dict['Data cache Maximum Utilization(%)'] = [cache_dict['Level 1']['max utilization(%)']]
    ret_dict['Data cache Average Utilization'] = [cache_dict['Level 1']['avg utilization']]

    # Reset registers
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}
    consts.reg_file['x2'] = config['profiles']['cfg']['stack_pointer']
    consts.reg_file['x3'] = config['profiles']['cfg']['global_pointer']

    # Return the final results
    return ret_dict


def instruction_cache_simulator(master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):

    '''
    Cache simulator for data cache.
    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - op_dict: A dictionary with the operations as keys and a list of
            InstructionEntry objects as values.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.
        
        Returns:
            - A dictionary with the cache level as keys and a list of cache utilization information as values.
        '''
    # Logging instruction cache statistics
    logger.info("Instruction Cache Statistics:")

    # Setting up memory and cache parameters
    no_of_sets = config['profiles']['cfg']['instr_cache']['no_of_sets']
    no_of_ways = config['profiles']['cfg']['instr_cache']['no_of_ways']
    line_size = config['profiles']['cfg']['instr_cache']['line_size']
    replacement_policy = config['profiles']['cfg']['instr_cache']['replacement_policy']

    # List of cache levels and dictionary to store cache utilization information
    cache_list = ['Level 1']
    cache_dict = {l: {'max utilization(%)': 0, "avg utilization": 0} for l in cache_list}

    # Dictionary to store the final results
    ret_dict = {'Instruction Cache': ['Level 1'], 'Instr cache Maximum Utilization(%)': [], 'Instr cache Average Utilization': []}
    # Creating the L1 instruction cache
    mem = MainMemory()
    l1 = Cache("L1", no_of_sets, no_of_ways, line_size, replacement_policy)
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)
    # Initializing minimum and maximum utilization
    min_util = max_util = cs.count_invalid_entries('L1')
    instr_util_list = []
    total_util = 0

    # Fixed byte length for instruction loading
    byte_length = 4

    # Loop through master instruction list
    for entry in master_inst_dict:
        if 'fence.i' in entry.instr_name:
            max_util *= line_size
            min_util *= line_size
            temp_total_util = ((max_util - min_util) / max_util) * 100
            instr_util_list.append(temp_total_util)
            if temp_total_util > total_util:
                total_util = temp_total_util
            cs.force_write_back("L1")
            cs.mark_all_invalid("L1")
            min_util = max_util = cs.count_invalid_entries("L1")

        # Load instruction address into the cache
        cs.load(entry.instr_addr, byte_length)
        
        # Update current utilization and track min/max values
        this_util = cs.count_invalid_entries('L1')
        max_util = max(max_util, this_util)
        min_util = min(min_util, this_util)

    # Print cache statistics
    cs.print_stats()

    # Calculate total utilization percentages
    max_util *= line_size
    min_util *= line_size
    temp_total_util = ((max_util - min_util) / max_util) * 100
    instr_util_list.append(temp_total_util)
    if temp_total_util > total_util:
        total_util = temp_total_util
    # Update cache utilization information
    cache_dict['Level 1']['max utilization(%)'] = total_util
    cache_dict['Level 1']['avg utilization'] = sum(instr_util_list)/len(instr_util_list)
    ret_dict['Instr cache Maximum Utilization(%)'] = [cache_dict['Level 1']['max utilization(%)']]
    ret_dict['Instr cache Average Utilization'] = [cache_dict['Level 1']['avg utilization']]

    # Reset registers
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}
    consts.reg_file['x2'] = config['profiles']['cfg']['stack_pointer']
    consts.reg_file['x3'] = config['profiles']['cfg']['global_pointer']

    # Return the final results
    return ret_dict
