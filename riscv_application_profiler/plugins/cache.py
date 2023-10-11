from cachesim import CacheSimulator, Cache, MainMemory, CacheVisualizer
import riscv_application_profiler.consts as consts
from riscv_isac.log import *
import itertools
import collections
import cachesim
import inspect

miss_address_dict = dict()
miss_inst_dict = dict()
stage1_dict = dict()
stage2_dict = dict()

def data_cache_simulator(master_inst_list: list, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
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

    # List of cache levels
    cache_list = ['Level 1']

    # Dictionary to store cache utilization information
    cache_dict = {l: {'utilization(%)': 0} for l in cache_list}

    # Dictionary to store the final results
    ret_dict = {'Data Cache': [f'{op}' for op in cache_list], 'Utilization(%)': []}

    # Setting up memory and cache parameters
    mem = MainMemory()
    no_of_sets = config['profiles']['cfg']['data_cache']['no_of_sets']
    no_of_ways = config['profiles']['cfg']['data_cache']['no_of_ways']
    line_size = config['profiles']['cfg']['data_cache']['line_size']
    cache_lines = no_of_sets * no_of_ways

    # Creating the L1 cache
    l1 = Cache("L1", no_of_sets, no_of_ways, line_size, "RR")
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)
    # Initializing minimum and maximum utilization
    min_util = max_util = cs.count_invalid_entries()

    additional_cycle = 0
    prev_hits = l1.backend.HIT_count

    prev_misses = l1.backend.MISS_count

    address_set = set()
    cacheable_data_start = int(config['profiles']['cfg']['data_cache']['range']['start'])
    cacheable_data_end = int(config['profiles']['cfg']['data_cache']['range']['end'])
    cacheable_instr_start = int(config['profiles']['cfg']['instr_cache']['range']['start'])
    cacheable_instr_end = int(config['profiles']['cfg']['instr_cache']['range']['end'])

    

    depth = 0
    dirty_lines_set = set()
    line_num = 0
    # Loop through instructions
    for i in master_inst_list:
        line_num += 1
        if 'fence' in i.instr_name:
            # print(dirty_lines_set)
            sorted_dirty_lines_set = tuple(sorted(dirty_lines_set))
            
            # print(sorted_dirty_lines_set)
            ops_dict['fence'][i] += 1 # to tell it's fence it takes one cycle
            master_inst_list[i] += 1

            ops_dict['fence'][i] += cache_lines # to check all lines
            master_inst_list[i] += cache_lines
            j=1
            for cache_line_num in sorted_dirty_lines_set:
                if (cache_line_num + cycle_accurate_config['cycles']['bus_latency']['data'] + cycle_accurate_config['cycles']['structural_hazards']['bus']) > cache_lines:
                    # to see if last few lines are dirty , and add cycles accordingly
                    additional_cycle += (cache_line_num + cycle_accurate_config['cycles']['bus_latency']['data'] + cycle_accurate_config['cycles']['structural_hazards']['bus']) - cache_lines
                    master_inst_list[i] += (cache_line_num + cycle_accurate_config['cycles']['bus_latency']['data'] + cycle_accurate_config['cycles']['structural_hazards']['bus']) - cache_lines
                if (j < len(sorted_dirty_lines_set)) and ((sorted_dirty_lines_set[j] - cache_line_num) < (cycle_accurate_config['cycles']['structural_hazards']['bus'])):
                    # to see if there is a gap between dirty lines
                    # print(cache_line_num,sorted_dirty_lines_set[j])
                    ops_dict['fence'][i] += (cycle_accurate_config['cycles']['structural_hazards']['bus']) - (sorted_dirty_lines_set[j] - cache_line_num)
                    master_inst_list[i] += (cycle_accurate_config['cycles']['structural_hazards']['bus']) - (sorted_dirty_lines_set[j] - cache_line_num)
                    # print((cycle_accurate_config['cycles']['bus_latency']['data'] - 1) - (sorted_dirty_lines_set[j] - cache_line_num))
                j=j+1

            cs.force_write_back()
            l1 = Cache("L1", no_of_sets, no_of_ways, line_size, "RR")
            cs = CacheSimulator(l1, mem)
            min_util = max_util = cs.count_invalid_entries()
            prev_hits = l1.backend.HIT_count
            prev_misses = l1.backend.MISS_count
            
            dirty_lines_set.clear()

        # Handle load/store instructions
        if i in ops_dict['loads'] or i in ops_dict['stores']:
            # Determine the address based on instruction type
            if 'sp' in i.instr_name:
                base = int(consts.reg_file['x2'], 16)
            else:
                rs = str(i.rs1[1]) + str(i.rs1[0])
                base = int(consts.reg_file.get(rs, consts.freg_file.get(rs, '0x0')), 16)
            if i.imm is None:
                address = base
            else:
                address = base + i.imm
            # Determine the byte length for the operation
            if ('d' in i.instr_name):
                byte_length = 8
            elif ('w' in i.instr_name):
                byte_length = 4
            elif ('h' in i.instr_name):
                byte_length = 2
            elif ('b' in i.instr_name):
                byte_length = 1

            address_set.add(address)
            
            # Handle load and store operations
            if i in ops_dict['loads']  :
                if (i.instr_addr >= cacheable_instr_start and i.instr_addr <= cacheable_instr_end) and (address >= cacheable_data_start and address <= cacheable_data_end):
                    
                    cl_id = address >> cs.last_level.backend.cl_bits
                    set_id = cl_id % cs.last_level.backend.sets
                    way_id = cl_id % cs.last_level.backend.ways
                    dirty_line = (set_id*no_of_ways) + way_id
                    dirty_lines_set.add(dirty_line+1)

                    cs.load(address, byte_length)
                    if prev_hits < l1.backend.HIT_count:
                        additional_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] - 1
                    elif prev_misses < l1.backend.MISS_count:
                        additional_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] - 1
                        miss_address_dict[line_num] = i
                    else:
                        additional_cycle = 0
                else:
                    additional_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] - 1
                ops_dict['loads'][i] = ops_dict['loads'][i] + additional_cycle
                master_inst_list[i] = master_inst_list[i] + additional_cycle
                    

            elif i in ops_dict['stores'] :
                if(i.instr_addr >= cacheable_instr_start and i.instr_addr <= cacheable_instr_end) and (address >= cacheable_data_start and address <= cacheable_data_end):

                    cl_id = address >> cs.last_level.backend.cl_bits
                    set_id = cl_id % cs.last_level.backend.sets
                    way_id = cl_id % cs.last_level.backend.ways
                    dirty_line = (set_id*no_of_ways) + way_id
                    dirty_lines_set.add(dirty_line+1)

                    cs.store(address, byte_length)
                    if prev_hits < l1.backend.HIT_count:
                        additional_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] - 1
                    elif prev_misses < l1.backend.MISS_count:
                        additional_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] - 1
                        miss_address_dict[line_num] = i
                    else:
                        additional_cycle = 0
                else:
                    additional_cycle = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss'] - 1
                ops_dict['stores'][i] = ops_dict['stores'][i] + additional_cycle
                master_inst_list[i] = master_inst_list[i] + additional_cycle
            
            prev_hits = l1.backend.HIT_count 
            prev_misses = l1.backend.MISS_count

            # Update current utilization and track min/max values
            this_util = cs.count_invalid_entries()
            max_util = max(max_util, this_util)
            min_util = min(min_util, this_util)

        # Handle register commits
        if i.reg_commit and i.reg_commit[1] != '0':
            consts.reg_file[f'x{i.rd[0]}'] = i.reg_commit[2]

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
    consts.reg_file['x2'] = '0x800030d0'
    consts.reg_file['x3'] = '0x800030d0'


    

    # Return the final results
    return ret_dict



def instruction_cache_simulator(master_inst_list: list, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
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
    no_of_sets = config['profiles']['cfg']['instr_cache']['no_of_sets']
    no_of_ways = config['profiles']['cfg']['instr_cache']['no_of_ways']
    line_size = config['profiles']['cfg']['instr_cache']['line_size']

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
    prev_hits = l1.backend.HIT_count
    prev_misses = l1.backend.MISS_count
    prev_last_stage_cycle = 0
    fetch_cycle = 0
    cacheable_start = int(config['profiles']['cfg']['instr_cache']['range']['start'])
    cacheable_end = int(config['profiles']['cfg']['instr_cache']['range']['end'])
    line_num = 0

    for entry in master_inst_list:
        line_num += 1
        stage2_dict[line_num] = 0
        # Load instruction address into the cache
        if (entry.instr_addr >= cacheable_start and entry.instr_addr <= cacheable_end):
            cs.load(entry.instr_addr, byte_length)
            if prev_hits < l1.backend.HIT_count:
                fetch_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['hit'] 
                prev_hits = l1.backend.HIT_count
            elif prev_misses < l1.backend.MISS_count:
                fetch_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['miss']
                prev_misses = l1.backend.MISS_count
        else:
            fetch_cycle = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['instruction']['miss']

        if (fetch_cycle - prev_last_stage_cycle) > 0:
            for op in ops_dict.keys():
                if entry in ops_dict[op]:
                    ops_dict[op][entry] = ops_dict[op][entry] + (fetch_cycle - prev_last_stage_cycle)
                    master_inst_list[entry] = master_inst_list[entry] + (fetch_cycle - prev_last_stage_cycle)

                    if line_num in miss_address_dict:
                        miss_address_dict[line_num] = master_inst_list[entry]
                    stage2_dict[line_num] = master_inst_list[entry]
                    # print (miss_address_dict[line_num])

                    prev_last_stage_cycle = master_inst_list[entry] - (fetch_cycle - prev_last_stage_cycle)
        else:
            prev_last_stage_cycle = master_inst_list[entry]
            if line_num in miss_address_dict:
                miss_address_dict[line_num] = 0
            
        
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
    consts.reg_file['x2'] = '0x800030d0'
    consts.reg_file['x3'] = '0x800030d0'

    # Return the final results
    mem_mem(master_inst_list, ops_dict, miss_address_dict, config, cycle_accurate_config, stage2_dict)
    return ret_dict


def mem_mem (master_inst_list, ops_dict, missed_address_dict, config, cycle_accurate_config, stage2_dict):
    '''
    Function to calculate the total cycles for memory operations
    Args:
        - ops_dict: A dictionary with the operations as keys and a list of
            InstructionEntry objects as values.
        
        Returns:
            - A dictionary with the operations as keys and the total cycles as values.
    '''


    data_cache_capacity = cycle_accurate_config['cycles']['structural_hazards']['data_cache']
    additional_length = 0
    overlaping_latency = 0
    words_in_line = config['profiles']['cfg']['data_cache']['line_size']//4
    line_num = 0
    change_in_stage2 = 0

    for entry in master_inst_list:
        if change_in_stage2 > 0:
            stage2_dict[line_num] = stage2_dict[line_num] - structural_latency
            master_inst_list[entry] =  master_inst_list[entry] - structural_latency
            change_in_stage2 = 0
        line_num += 1
        if entry in ops_dict['loads'] or entry in ops_dict['stores']:

            # checking first mem inst is a miss
            if line_num in missed_address_dict:

                if (additional_length - (overlaping_latency + miss_address_dict[line_num])) > 0:
                    structural_latency = additional_length - overlaping_latency
                    if entry in ops_dict['loads']:
                        ops_dict['loads'][entry] += structural_latency
                        master_inst_list[entry] += structural_latency
                        if (line_num+1 in stage2_dict) and (stage2_dict[line_num+1] - structural_latency) > 0:
                            change_in_stage2 = stage2_dict[line_num+1] - ops_dict['loads'][entry]
                            

                    else:
                        ops_dict['stores'][entry] += structural_latency
                        master_inst_list[entry] += structural_latency
                        if (line_num+1 in stage2_dict) and (stage2_dict[line_num+1] - structural_latency) > 0:
                            change_in_stage2 = stage2_dict[line_num+1] - ops_dict['stores'][entry]
                            


                additional_length = words_in_line - data_cache_capacity
                overlaping_latency = 0

            else:

                    
                if (additional_length - overlaping_latency) > 0:
                    structural_latency = additional_length - overlaping_latency
                    # print(additional_length - overlaping_latency)
                    if entry in ops_dict['loads']:
                        ops_dict['loads'][entry] += structural_latency
                        master_inst_list[entry] += structural_latency
                        if (line_num+1 in stage2_dict) and (stage2_dict[line_num+1] - structural_latency) > 0:
                            change_in_stage2 = stage2_dict[line_num+1] - ops_dict['loads'][entry]
                           
                    else:
                        ops_dict['stores'][entry] += structural_latency
                        master_inst_list[entry] += structural_latency
                        if (line_num+1 in stage2_dict) and (stage2_dict[line_num+1] - structural_latency) > 0:
                            change_in_stage2 = stage2_dict[line_num+1] - ops_dict['stores'][entry]
                            
                    additional_length = 0
                    overlaping_latency = 0

        else:
            overlaping_latency += master_inst_list[entry]

                    

                

                
            
    
    