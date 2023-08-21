from cachesim import CacheSimulator, Cache, MainMemory
import riscv_application_profiler.consts as consts
from riscv_isac.log import *

def data_cache_simulator(master_inst_list, op_dict):
    '''
    Cache simulator for data cache.
    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - op_dict: A dictionary with the operations as keys and a list of
            InstructionEntry objects as values.
        
        Returns:
            - A list of cache names and a dictionary with the cache names as keys 
              and a dictionary with the cache statistics as values.
        '''
    # Logging cache statistics
    logger.info("Data Cache Statistics:")

    # Lists of load and store operations
    load_list = op_dict['loads']
    store_list = op_dict['stores']

    # List of cache levels
    cache_list = ['Level 1']

    # Dictionary to store cache utilization information
    cache_dict = {l: {'utilization(%)': 0} for l in cache_list}

    # Dictionary to store the final results
    ret_dict = {'Data Cache': [f'{op}' for op in cache_list], 'Utilization(%)': []}

    # Setting up memory and cache parameters
    mem = MainMemory()
    no_of_sets = 64
    no_of_ways = 4
    line_size = 64

    # Creating the L1 cache
    l1 = Cache("L1", no_of_sets, no_of_ways, line_size, "RR")
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)

    # Initializing minimum and maximum utilization
    min_util = max_util = cs.count_invalid_entries()

    # Loop through instructions
    for i in master_inst_list:
        # Handle register commits
        if i.reg_commit and i.reg_commit[1] != '0':
            consts.reg_file[f'x{i.rd[1]}'] = i.reg_commit[2]
        
        # Handle load/store instructions
        if i in load_list or i in store_list:
            # Determine the address based on instruction type
            if 'sp' in i.instr_name:
                address = int(consts.reg_file['x2'], 16) + (i.imm or 0)
            else:
                rs = str(i.rs1[1]) + str(i.rs1[0])
                base = int(consts.reg_file.get(rs, consts.freg_file.get(rs, '0x0')), 16)
                address = base + (i.imm or 0)
            
            # Determine the byte length for the operation
            byte_lengths = {'d': 8, 'w': 4, 'h': 2, 'b': 1}
            byte_length = byte_lengths.get(i.instr_name[-1], 0)
            
            # Handle load and store operations
            if i in load_list:
                cs.load(address, byte_length)
            elif i in store_list:
                cs.store(address, byte_length)

            # Update current utilization and track min/max values
            this_util = cs.count_invalid_entries()
            max_util = max(max_util, this_util)
            min_util = min(min_util, this_util)

    # Print cache statistics
    cs.print_stats()

    # Calculate total utilization percentages
    max_util *= line_size
    min_util *= line_size
    total_util = ((max_util - min_util) / max_util) * 100

    # Update cache utilization information
    cache_dict['Level 1']['utilization(%)'] = total_util
    ret_dict['Utilization(%)'] = [cache_dict[cache]['utilization(%)'] for cache in cache_list]

    # Reset registers
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}
    consts.reg_file['x2'] = '0x7ffffff0'
    consts.reg_file['x3'] = '0x100000'

    # Return the final results
    return ret_dict



def instruction_cache_simulator(master_inst_list):
    '''
    Cache simulator for instruction cache.
    Args:
        - master_inst_list: A list of InstructionEntry objects.
        
        Returns:
            - A list of cache names and a dictionary with the cache names as keys
              and a dictionary with the cache statistics as values.
    
    '''
    # Logging instruction cache statistics
    logger.info("Instruction Cache Statistics:")

    # Setting up memory and cache parameters
    mem = MainMemory()
    no_of_sets = 64
    no_of_ways = 4
    line_size = 64

    # List of cache levels and dictionary to store cache utilization information
    cache_list = ['Level 1']
    cache_dict = {l: {'utilization(%)': 0} for l in cache_list}

    # Dictionary to store the final results
    ret_dict = {'Instruction Cache': [f'{op}' for op in cache_list], 'Utilization(%)': []}

    # Creating the L1 instruction cache
    l1 = Cache("L1", no_of_sets, no_of_ways, line_size, "LRU")
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)

    # Initializing minimum and maximum utilization
    min_util = max_util = cs.count_invalid_entries()

    # Fixed byte length for instruction loading
    byte_length = 4

    # Loop through master instruction list
    for entry in master_inst_list:
        # Load instruction address into the cache
        cs.load(entry.instr_addr, byte_length)
        
        # Update current utilization and track min/max values
        this_util = cs.count_invalid_entries()
        max_util = max(max_util, this_util)
        min_util = min(min_util, this_util)

    # Print cache statistics
    cs.print_stats()

    # Calculate total utilization percentages
    max_util *= line_size
    min_util *= line_size
    total_util = ((max_util - min_util) / max_util) * 100

    # Update cache utilization information
    cache_dict['Level 1']['utilization(%)'] = total_util
    ret_dict['Utilization(%)'] = [cache_dict[cache]['utilization(%)'] for cache in cache_list]

    # Reset registers
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}
    consts.reg_file['x2'] = '0x7ffffff0'
    consts.reg_file['x3'] = '0x100000'

    # Return the final results
    return ret_dict


