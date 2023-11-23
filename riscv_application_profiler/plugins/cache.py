from cachesim import CacheSimulator, Cache, MainMemory
import riscv_application_profiler.consts as consts
from riscv_isac.log import *

miss_address_dict = dict()
stage2_dict = dict()
stage1_dict = dict()
data_cache_status = dict()
mem_mem_dict = dict()

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
    logger.info("Computing Data Cache Statistics.")

    # List of cache levels
    cache_list = ['Level 1']

    # Dictionary to store cache utilization information
    cache_dict = {"data_l1": {'max utilization(%)': 0, "avg utilization": 0} }

    total_util = 0
    cache_util_list = []

    # Dictionary to store the final results
    ret_dict = {'Data Cache': ['Level 1'], 'Maximum Utilization(%)': [], 'Average Utilization': [], 'Miss Rate': [], 'Hit Rate': []}
    # mem,cs,l1 = cache_setup('data', config)


    no_of_sets = config['profiles']['cfg']['data_cache']['no_of_sets']
    no_of_ways = config['profiles']['cfg']['data_cache']['no_of_ways']
    line_size = config['profiles']['cfg']['data_cache']['line_size']
    replacement_policy = config['profiles']['cfg']['data_cache']['replacement_policy']
    total_cache_line = no_of_sets * no_of_ways
    number_of_words_in_line = line_size//4 # line size in byptes / 4 bytes (word size)


    # Creating the L1 cache
    mem = MainMemory()
    l1 = Cache("L1", no_of_sets, no_of_ways, line_size, replacement_policy)
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)
    # Initializing minimum and maximum utilization
    min_util = max_util = cs.count_invalid_entries("L1")

    additional_cycle = 0
    prev_hits = l1.backend.HIT_count

    prev_misses = l1.backend.MISS_count

    cacheable_data_start = int(config['profiles']['cfg']['data_cache']['range']['start'])
    cacheable_data_end = int(config['profiles']['cfg']['data_cache']['range']['end'])
    cacheable_instr_start = int(config['profiles']['cfg']['instr_cache']['range']['start'])
    cacheable_instr_end = int(config['profiles']['cfg']['instr_cache']['range']['end'])

    hit_address_line_num = miss_address_line_num = 0
    last_mem_line_no = 0
    mem_mem_delay = 0

    d_miss_count = d_hit_count = 0
    
    dirty_lines_set = set() # to keep track of dirty lines
    line_num = 0 # to keep track of instruction/line number
    # Loop through instructions
    for entry in master_inst_dict:
        line_num += 1 
        if 'fence' in entry.instr_name:
            if cycle_accurate_config != None:

                invalid_entries = cs.count_invalid_entries("L1") 
                temp_total_util = ((total_cache_line - invalid_entries) / total_cache_line) * 100
                cache_util_list.append(temp_total_util)
                if temp_total_util > total_util:
                    total_util = temp_total_util
                

                dirty_lines_set = cs.dirty_cl_ids('L1')
                # sorting the dirty lines set, as fence instruction traverse the cache in sorted order
                sorted_dirty_lines_set = tuple(sorted(dirty_lines_set))

                ops_dict['fence'][entry] += 1 # one cycle for fence instruction
                master_inst_dict[entry] += 1

                ops_dict['fence'][entry] += total_cache_line # each cache line takes one cycle
                master_inst_dict[entry] += total_cache_line
                dirty_line_index=1 # used to get the next dirty line
                for cache_line in sorted_dirty_lines_set:
                    if (cache_line + cycle_accurate_config['cycles']['bus_latency']['data'] + (number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'])) > total_cache_line:
                        # to see if last few lines are dirty , and add cycles accordingly 
                        master_inst_dict[entry] += (cache_line + cycle_accurate_config['cycles']['bus_latency']['data'] + (number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'])) - total_cache_line
                    if (dirty_line_index < len(sorted_dirty_lines_set)) and ((sorted_dirty_lines_set[dirty_line_index] - cache_line) < number_of_words_in_line): 
                        # to see if there is a gap between dirty lines that are less than the number of words in a line(structural hazard)
                        ops_dict['fence'][entry] += (number_of_words_in_line ) - (sorted_dirty_lines_set[dirty_line_index] - cache_line)
                        master_inst_dict[entry] += (number_of_words_in_line ) - (sorted_dirty_lines_set[dirty_line_index] - cache_line)
                    dirty_line_index=dirty_line_index+1

            # sort of creating afresh cache, as fence instruction invalidates the cache
            d_miss_count += l1.backend.MISS_count
            d_hit_count += l1.backend.HIT_count
            # cs.force_write_back()
            cs.mark_all_invalid("L1")
            min_util = max_util = cs.count_invalid_entries("L1")
            prev_hits = l1.backend.HIT_count
            prev_misses = l1.backend.MISS_count
            
            # clearing the dirty lines set as cache is empty after fence instruction
            dirty_lines_set.clear()

        

        # Handle load/store instructions
        if entry in ops_dict['loads'] or entry in ops_dict['stores']:
                
            # Determine the address based on instruction type
            if 'sp' in entry.instr_name:
                # taking value from x2 as it infers the stack pointer
                base = int(consts.reg_file['x2'], 16)
            else:
                rs = str(entry.rs1[1]) + str(entry.rs1[0]) # gives the register name which is used as base address
                base = int(consts.reg_file.get(rs, consts.freg_file.get(rs, '0x0')), 16)
                    
            # check if immediate value is present
            if entry.imm is None:
                address = base
            else:
                address = base + entry.imm
            # print (i, hex(address), hex(base))

            last_mem_line_no = line_num

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
            if entry in ops_dict['loads']  :
                if (entry.instr_addr >= cacheable_instr_start and entry.instr_addr <= cacheable_instr_end) and (address >= cacheable_data_start and address <= cacheable_data_end):
                    # checking if the address is in cacheable range
                    cs.load(address, byte_length)
                    if cycle_accurate_config != None:
                        # checking if it's a miss, l1.backend.MISS_count is incremented after a store only when it's a miss
                        if prev_misses < l1.backend.MISS_count:
                            
                            # miss latency allocation
                            ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                            master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 

                            # since data cache is partial critical workd first, we need to see if previous miss is still busy filling the cache line
                            # if it's busy then we need to add cycles to the current instruction
                            if line_num - miss_address_line_num > 0 and miss_address_line_num != 0:
                                if (line_num - miss_address_line_num) < number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache']:
                                    for add_len in range(0,line_num - miss_address_line_num,cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
                                        # keeping track of how many instructions will data cache be busy in case it's a miss, considering each fill takes one cycle
                                        data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
                                    master_inst_dict[entry] = master_inst_dict[entry] + (number_of_words_in_line - (line_num - miss_address_line_num))
                                    ops_dict['loads'][entry] = ops_dict['loads'][entry] + (number_of_words_in_line - (line_num - miss_address_line_num))
                                    mem_mem_dict[line_num] = (number_of_words_in_line - (line_num - miss_address_line_num))

                            miss_address_line_num = line_num # keeping track of the instruction number that caused a miss

                            data_cache_status[line_num] = number_of_words_in_line

                            # keeping track of instructions that cused a data cache miss and the instruction number
                            miss_address_dict[line_num] = entry


                        elif prev_hits <= l1.backend.HIT_count:
                            # checking if it's a hit, l1.backend.HIT_count is incremented or remains same after a store only when it's a hit
                            ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                            master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                            hit_address_line_num = line_num
                            if hit_address_line_num - miss_address_line_num > 0 and miss_address_line_num != 0:
                                # data cache will complete writing in the instruction causes a hit in the data cache
                                if (hit_address_line_num - miss_address_line_num) < number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache']:
                                    for add_len in range(0,hit_address_line_num - miss_address_line_num,cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
                                        # keeping track of how many instructions will data cache be busy in case it's a miss, considering each fill takes one cycle
                                        data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
                                    master_inst_dict[entry] = master_inst_dict[entry] + (number_of_words_in_line - (hit_address_line_num - miss_address_line_num))
                                    ops_dict['loads'][entry] = ops_dict['loads'][entry] + (number_of_words_in_line - (hit_address_line_num - miss_address_line_num)) 
                                    mem_mem_dict[line_num] = (number_of_words_in_line - (hit_address_line_num - miss_address_line_num))
                                else:
                                    for add_len in range(0,number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'],cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
                                        # keeping track of how many instructions will data cache be busy in case it's a miss, considering each fill takes one cycle
                                        data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
                                miss_address_line_num = 0

                else:
                    if cycle_accurate_config != None:
                        # all non cacheable address access is a miss
                        ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                        master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                    

            elif entry in ops_dict['stores'] :
                if(entry.instr_addr >= cacheable_instr_start and entry.instr_addr <= cacheable_instr_end) and (address >= cacheable_data_start and address <= cacheable_data_end):
                    # checking if the address is in cacheable range\
                    cs.store(address, byte_length)

                    if cycle_accurate_config != None:
                        if prev_misses < l1.backend.MISS_count:

                            # checking if it's a miss, l1.backend.MISS_count is incremented after a store only when it's a miss
                            ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                            master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 

                            if line_num - miss_address_line_num > 0 and miss_address_line_num != 0:
                                if (line_num - miss_address_line_num) < number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache']:
                                    for add_len in range(0,line_num - miss_address_line_num,cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
                                        # keeping track of how many instructions will data cache be busy in cse it's a miss, considering each fill takes one cycle
                                        data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
                                    master_inst_dict[entry] = master_inst_dict[entry] + (number_of_words_in_line - (line_num - miss_address_line_num))
                                    ops_dict['stores'][entry] = ops_dict['stores'][entry] + (number_of_words_in_line - (line_num - miss_address_line_num))
                                    mem_mem_dict[line_num] = (number_of_words_in_line - (line_num - miss_address_line_num))

                            miss_address_line_num = line_num

                            data_cache_status[line_num] = number_of_words_in_line

                            # keeping track of instructions that cused a data cache miss and the instruction number
                            miss_address_dict[line_num] = entry

                        elif prev_hits <= l1.backend.HIT_count:
                            # checking if it's a hit, l1.backend.HIT_count is incremented or remains same after a store only when it's a hit
                            ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                            master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit']
                            hit_address_line_num = line_num
                            if hit_address_line_num - miss_address_line_num > 0 and miss_address_line_num != 0:
                                # data cache will complete writing in the instruction causes a hit in the data cache
                                if (hit_address_line_num - miss_address_line_num) < number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache']:
                                    for add_len in range(0,hit_address_line_num - miss_address_line_num,cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
                                        # keeping track of how many instructions will data cache be busy in cse it's a miss, considering each fill takes one cycle
                                        data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
                                    master_inst_dict[entry] = master_inst_dict[entry] + (number_of_words_in_line - (hit_address_line_num - miss_address_line_num))
                                    ops_dict['stores'][entry] = ops_dict['stores'][entry] + (number_of_words_in_line - (hit_address_line_num - miss_address_line_num)) 
                                    mem_mem_dict[line_num] = (number_of_words_in_line - (hit_address_line_num - miss_address_line_num))
                                else:
                                    for add_len in range(0,number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'],cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
                                        # keeping track of how many instructions will data cache be busy in cse it's a miss, considering each fill takes one cycle
                                        data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
                                miss_address_line_num = 0


                else:
                    if cycle_accurate_config != None:
                        # all non cacheable address access is a miss
                        ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                        master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
            
            
            
            # keeping track of previous hits and misses, used for knowing the current address is a hit or a miss
            prev_hits = l1.backend.HIT_count 
            prev_misses = l1.backend.MISS_count

            # Update current utilization and track min/max values
            this_util = cs.count_invalid_entries("L1")
            max_util = max(max_util, this_util)
            min_util = min(min_util, this_util)

        # Handle register commits
        if entry.reg_commit and entry.reg_commit[1] != '0':
            consts.reg_file[f'x{int(entry.reg_commit[1])}'] = entry.reg_commit[2] 

    # Calculate total utilization percentages
    invalid_entries = cs.count_invalid_entries("L1")
    temp_total_util = ((total_cache_line - invalid_entries) / total_cache_line) * 100
    cache_util_list.append(temp_total_util)
    if temp_total_util > total_util:
        total_util = temp_total_util

    d_miss_count += l1.backend.MISS_count
    d_hit_count += l1.backend.HIT_count

    # Update cache utilization information
    cache_dict['data_l1']['max utilization(%)'] = total_util
    cache_dict['data_l1']['avg utilization'] = sum(cache_util_list)/len(cache_util_list)
    ret_dict['Maximum Utilization(%)'] = [cache_dict['data_l1']['max utilization(%)']]
    ret_dict['Average Utilization'] = [cache_dict['data_l1']['avg utilization']]
    ret_dict['Miss Rate'] = [(d_miss_count/(d_miss_count+d_hit_count))*100]
    ret_dict['Hit Rate'] = [(d_hit_count/(d_miss_count+d_hit_count))*100]

    # Reset registers
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}

    logger.info("Done.")

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
    logger.info("Computing Instruction Cache Statistics.")

    # Setting up memory and cache parameters
    no_of_sets = config['profiles']['cfg']['instr_cache']['no_of_sets']
    no_of_ways = config['profiles']['cfg']['instr_cache']['no_of_ways']
    line_size = config['profiles']['cfg']['instr_cache']['line_size']
    total_cache_line = no_of_sets * no_of_ways
    replacement_policy = config['profiles']['cfg']['instr_cache']['replacement_policy']
    number_of_words_in_line = line_size//4 # line size in byptes / 4 bytes (word size)


    # List of cache levels and dictionary to store cache utilization information
    cache_list = ['Level 1']
    cache_dict = {"instr_l1": {'max utilization(%)': 0, "avg utilization": 0} }


    total_util = 0
    cache_util_list = []

    # Dictionary to store the final results
    ret_dict = {'Instruction Cache': ['Level 1'], 'Maximum Utilization(%)': [], 'Average Utilization': [], 'Miss Rate': [], 'Hit Rate': []}

    i_miss_count = i_hit_count = 0

    # Creating the L1 instruction cache
    mem = MainMemory()
    l1 = Cache("L1", no_of_sets, no_of_ways, line_size, replacement_policy)
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)

    # Initializing minimum and maximum utilization
    min_util = max_util = cs.count_invalid_entries("L1")


    # Loop through master instruction list
    prev_hits = l1.backend.HIT_count
    prev_misses = l1.backend.MISS_count
    prev_last_stage_cycle = 0
    fetch_cycle = 0
    cacheable_start = int(config['profiles']['cfg']['instr_cache']['range']['start'])
    cacheable_end = int(config['profiles']['cfg']['instr_cache']['range']['end'])
    # keeping track of instruction/line number
    line_num = 0
    keys_to_delete = {}
    # print(data_cache_status)
    
    for entry in master_inst_dict:

        # Handle fence instructions
        if 'fence.i' in entry.instr_name:
            if cycle_accurate_config != None:
                invalid_entries = cs.count_invalid_entries('L1')
                temp_total_util = ((total_cache_line - invalid_entries) / total_cache_line) * 100
                cache_util_list.append(temp_total_util)
                if temp_total_util > total_util:
                    total_util = temp_total_util

                # flush i cache
                master_inst_dict[entry] += total_cache_line

            # invalidating the cache and flushing the pipeline
            # invalidation happens in IF stage and flushing happens in WB stage
            i_miss_count += l1.backend.MISS_count
            i_hit_count += l1.backend.HIT_count
            cs.mark_all_invalid('L1')
            min_util = max_util = cs.count_invalid_entries('L1')
            prev_hits = l1.backend.HIT_count
            prev_misses = l1.backend.MISS_count
            
        # Determine the byte length for the operation
        if 'c.' in entry.instr_name:
            # compressed instructions are 2 bytes
            byte_length = 2
        else:
            # all other instructions are 4 bytes
            byte_length = 4

        line_num += 1
        stage1_dict[line_num] = 0 # to keep track of stage1 cycles

        # straddle check variables, stradde delay gives extra cycles when straddele occurs
        straddle_check_hit = straddle_check_miss = straddle_delay = 0 

        # Load instruction address into the cache
        if (entry.instr_addr >= cacheable_start and entry.instr_addr <= cacheable_end):
            # checking if the instruction address is in cacheable range
            
            cs.load(entry.instr_addr, byte_length)
            if cycle_accurate_config != None:
            
                if prev_hits < l1.backend.HIT_count:
                    # checking if it's a hit, l1.backend.HIT_count is incremented after a load only when it's a hit
                    fetch_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['hit']
                    # when straddle occurs, and it's a hit then it's a hit in two cache lines. Therefore straddle_check_hit get's incremented by 2
                    # There might be a sdraddle miss then it's a hit on one cahce line and miss on another cache line. Therefore straddle_check_hit get's incremented by 1
                    straddle_check_hit = l1.backend.HIT_count - prev_hits
                    # keeping track of previous hits, used for knowing the current address is a hit or a miss
                    prev_hits = l1.backend.HIT_count  

                # replaced elif with if because of cache line straddling
                if prev_misses < l1.backend.MISS_count:
                    # checking if it's a miss, l1.backend.MISS_count is incremented after a load only when it's a miss
                    fetch_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['miss']
                    # when straddle occurs, and it's a miss then it's a miss in two cache lines. Therefore straddle_check_miss get's incremented by 2
                    # There might be a sdraddle hit then it's a miss on one cahce line and hit on another cache line. Therefore straddle_check_miss get's incremented by 1
                    straddle_check_miss += l1.backend.MISS_count - prev_misses
                    # keeping track of previous misses, used for knowing the current address is a hit or a miss
                    prev_misses = l1.backend.MISS_count

                if straddle_check_hit == 1 and straddle_check_miss == 1:
                    # its straddle and a miss on one line and hit on another line
                    straddle_delay = 2 # delay for the above case
                    fetch_cycle = fetch_cycle + 2
                elif straddle_check_hit == 2 and straddle_check_miss == 0:
                    # its straddle and a hit on both lines
                    straddle_delay = 1 # delay for the above case
                    fetch_cycle = fetch_cycle + 1
                elif straddle_check_hit == 0 and straddle_check_miss == 2: # not sure about this case
                    # its straddle and a miss on both lines
                    straddle_delay = 1 
                    fetch_cycle = fetch_cycle + cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['miss'] + 1

                stage1_dict[line_num] = fetch_cycle  
        else:
            if cycle_accurate_config != None:
                # all non cacheable pc address access is a miss
                fetch_cycle = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['instruction']['miss']
            
        # fetching and filling of cache can be done parallely, 
        # if current instr is a cache miss and and the bus is still busy filling the data cache 
        # then we finish filling the data the cache fully as we do instr fetch
        # so the instr which were busy filling the data cache should be removed from data cache status
        if cycle_accurate_config != None:
            if line_num in data_cache_status:
                if fetch_cycle > (data_cache_status[line_num]):
                    i = 0
                    if data_cache_status[line_num] >= number_of_words_in_line - 1 and (line_num - 1) in data_cache_status:
                        keys_to_delete[line_num] = data_cache_status[line_num - 1] - 1
                    elif data_cache_status[line_num] < number_of_words_in_line :
                        keys_to_delete[line_num] = data_cache_status[line_num]
                    for i in range(1, data_cache_status[line_num]):
                        if (line_num + i) in data_cache_status:
                            if data_cache_status[line_num + i] >= data_cache_status[line_num]:
                                break
                            else:
                                # keys_to_delete[line_num + i] = data_cache_status[line_num + i]
                                continue
                    if (line_num + i - 1) in data_cache_status:
                        
                        keys_to_delete[line_num + i] = data_cache_status[line_num + i - 1] - 1

                    # print(keys_to_delete)
            
            if line_num in keys_to_delete:
                if line_num in mem_mem_dict:
                    master_inst_dict[entry] = master_inst_dict[entry] - keys_to_delete[line_num]
                elif keys_to_delete[line_num] > cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['hit']:
                    master_inst_dict[entry] = master_inst_dict[entry] + keys_to_delete[line_num] 

            
            # checking if fetch cycle is greater than previous last stage cycle

            if (fetch_cycle - prev_last_stage_cycle) > 0 :
                # checking if fetching of instruction ahs to be stalled
                # if prev_last_stage_cycle is greater, then fetch will be completed as previous stage is completed
                for op in ops_dict.keys():
                    if entry in ops_dict[op]:
                    
                        ops_dict[op][entry] = ops_dict[op][entry] + (fetch_cycle - prev_last_stage_cycle)
                        master_inst_dict[entry] = master_inst_dict[entry] + (fetch_cycle - prev_last_stage_cycle)
                        stage1_dict[line_num] = fetch_cycle - prev_last_stage_cycle

                        if line_num in miss_address_dict:
                            miss_address_dict[line_num] = master_inst_dict[entry]


                        stage2_dict[line_num] = master_inst_dict[entry] - stage1_dict[line_num]
                        prev_last_stage_cycle = master_inst_dict[entry] - stage1_dict[line_num]
            else:
                prev_last_stage_cycle = master_inst_dict[entry]
            
        
        # Update current utilization and track min/max values
        this_util = cs.count_invalid_entries("L1")
        max_util = max(max_util, this_util)
        min_util = min(min_util, this_util)

    # Calculate total utilization percentages
    invalid_entries = cs.count_invalid_entries("L1")
    temp_total_util = ((total_cache_line - invalid_entries) / total_cache_line) * 100
    cache_util_list.append(temp_total_util)
    if temp_total_util > total_util:
        total_util = temp_total_util
    
    i_miss_count += l1.backend.MISS_count
    i_hit_count += l1.backend.HIT_count

    # Update cache utilization information
    cache_dict['instr_l1']['max utilization(%)'] = total_util
    cache_dict['instr_l1']['avg utilization'] = sum(cache_util_list)/len(cache_util_list)
    ret_dict['Maximum Utilization(%)'] = [cache_dict['instr_l1']['max utilization(%)']]
    ret_dict['Average Utilization'] = [cache_dict['instr_l1']['avg utilization']]
    ret_dict['Miss Rate'] = [(i_miss_count/(i_miss_count+i_hit_count))*100]
    ret_dict['Hit Rate'] = [(i_hit_count/(i_miss_count+i_hit_count))*100]

    # Reset registers
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}

    logger.info("Done.")

    # Return the final results
    return ret_dict











# L2 unified cache
def unified_L2_cache_simulator(master_inst_dict: list, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
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
    logger.info("Computing Muti Level Cache Statistics.")

    try:
        config['profiles']['cfg']['l2_cache']
    except KeyError:
        logger.error("L2 cache configuration not found.")
        return None
    try:
        cycle_accurate_config['cycles']['mem_latency']['l2']
    except KeyError:
        logger.error("L2 cache cycle accurate configuration not found.")
        return None
    
    # List of cache levels
    cache_list = ['Level 1']

    # Dictionary to store cache utilization information
    cache_dict = {"data_d_l1": {'max utilization(%)': 0, "avg utilization": 0} }

    total_util = 0
    total_util1 = 0
    cache_util_list = []

    # Dictionary to store the final results
    ret_dict_d = {'Data Cache': ['Level 1'], 'Data cache Maximum Utilization(%)': [], 'Data cache Average Utilization': [], 'Miss Rate': [], 'Hit Rate': []}
    # mem,cs,d_l1 = cache_setup('data', config)


    no_of_sets = config['profiles']['cfg']['data_cache']['no_of_sets']
    no_of_ways = config['profiles']['cfg']['data_cache']['no_of_ways']
    line_size = config['profiles']['cfg']['data_cache']['line_size']
    dCache_replacement_policy = config['profiles']['cfg']['data_cache']['replacement_policy']
    total_cache_line = no_of_sets * no_of_ways
    d_cache_load_from = config['profiles']['cfg']['data_cache']['load_from']
    d_cache_store_to = config['profiles']['cfg']['data_cache']['store_to']
    number_of_words_in_line = line_size//4 # line size in byptes / 4 bytes (word size)


    l2_no_of_sets = config['profiles']['cfg']['l2_cache']['no_of_sets']
    l2_no_of_ways = config['profiles']['cfg']['l2_cache']['no_of_ways']
    l2_line_size = config['profiles']['cfg']['l2_cache']['line_size']
    l2_replacement_policy = config['profiles']['cfg']['l2_cache']['replacement_policy']
    l2_total_cache_line = l2_no_of_sets * l2_no_of_ways
    l2_number_of_words_in_line = l2_line_size//4 # line size in byptes / 4 bytes (word size)

    # Creating the d_l1 cache
    mem = MainMemory()
    l2 = Cache("l2", l2_no_of_sets, l2_no_of_ways, l2_line_size, l2_replacement_policy)
    mem.load_to(l2)
    mem.store_from(l2)
    ret_dict2 = {'L2 Cache': ['Level 2'], 'L2 cache Maximum Utilization(%)': [], 'L2 cache Average Utilization': [], 'Miss Rate': [], 'Hit Rate': []}
    cache_util_list2 = []
    cache_dictl2 = {"l2": {'max utilization(%)': 0, "avg utilization": 0} }


    d_l1 = Cache("d_l1", no_of_sets, no_of_ways, line_size, dCache_replacement_policy, load_from=d_cache_load_from, store_to=d_cache_store_to)
    cs = CacheSimulator(d_l1, mem)

    prev_hits = d_l1.backend.HIT_count

    prev_misses = d_l1.backend.MISS_count

    cacheable_data_start = int(config['profiles']['cfg']['data_cache']['range']['start'])
    cacheable_data_end = int(config['profiles']['cfg']['data_cache']['range']['end'])
    cacheable_instr_start = int(config['profiles']['cfg']['instr_cache']['range']['start'])
    cacheable_instr_end = int(config['profiles']['cfg']['instr_cache']['range']['end'])
    
    dirty_lines_set = set() # to keep track of dirty lines
    line_num = 0 # to keep track of instruction/line number



    logger.info("Instruction Cache Statistics:")

    # Setting up memory and cache parameters
    no_of_sets1 = config['profiles']['cfg']['instr_cache']['no_of_sets']
    no_of_ways1 = config['profiles']['cfg']['instr_cache']['no_of_ways']
    line_size1 = config['profiles']['cfg']['instr_cache']['line_size']
    total_cache_line1 = no_of_sets1 * no_of_ways1
    icache_load_from = config['profiles']['cfg']['instr_cache']['load_from']
    icache_store_to = config['profiles']['cfg']['instr_cache']['store_to']
    iCache_replacement_policy = config['profiles']['cfg']['instr_cache']['replacement_policy']
    number_of_words_in_line1 = line_size1//4 # line size in byptes / 4 bytes (word size)


    # List of cache levels and dictionary to store cache utilization information
    cache_list1 = ['Level 1']
    cache_dict1 = {"instr_l1": {'max utilization(%)': 0, "avg utilization": 0} }


    total_util1 = 0
    cache_util_list1 = []
    

    # Dictionary to store the final results
    ret_dict_i = {'Instruction Cache': ['Level 1'], 'Instr cache Maximum Utilization(%)': [], 'Instr cache Average Utilization': [], 'Miss Rate': [], 'Hit Rate': []}


    
    i_l1 = Cache("i_l1", no_of_sets1, no_of_ways1, line_size1, iCache_replacement_policy, load_from=icache_load_from, store_to=icache_store_to)
    cs1 = CacheSimulator(i_l1, mem)


    # Loop through master instruction list
    prev_hits1 = i_l1.backend.HIT_count
    prev_misses1 = i_l1.backend.MISS_count
    prev_last_stage_cycle1 = 0
    fetch_cycle1 = 0
    cacheable_start1 = int(config['profiles']['cfg']['instr_cache']['range']['start'])
    cacheable_end1 = int(config['profiles']['cfg']['instr_cache']['range']['end'])
    # keeping track of instruction/line number
    # line_num = 0
    keys_to_delete1 = {}
    # print(data_cache_status)


    l2_prev_hits = l2.backend.HIT_count
    l2_prev_misses = l2.backend.MISS_count
    l2_total_util = 0

    data_cache_util_check = cs.count_invalid_entries('d_l1')
    instr_cache_util_check = cs1.count_invalid_entries('i_l1')
    dirty_cl_id_set = set()

    dl1_miss=il1_miss=l2_miss=0
    dl1_hit=il1_hit=l2_hit=0

    # Loop through instructions
    for entry in master_inst_dict:
        line_num += 1 
        if 'fence' in entry.instr_name:
            if cycle_accurate_config != None:
                d_l1_dirty_lines = cs.dirty_cl_ids('d_l1')
                l2_dirty_lines = cs.dirty_cl_ids('l2')

                data_invalid_entries = cs.count_invalid_entries('d_l1')
                data_temp_total_util = ((total_cache_line - data_invalid_entries) / total_cache_line) * 100
                cache_util_list.append(data_temp_total_util)
                if data_temp_total_util > total_util:
                    total_util = data_temp_total_util

                l2_invalid_lines = cs.count_invalid_entries('l2')
                temp_l2_util = ((l2_total_cache_line - l2_invalid_lines) / l2_total_cache_line)* 100
                cache_util_list2.append(temp_l2_util)
                if temp_l2_util > l2_total_util:
                    l2_total_util = temp_l2_util


                # sorting the dirty lines set, as fence instruction traverse the cache in sorted order
                # sorted_dirty_lines_set = tuple(sorted(dirty_lines_set))

                ops_dict['fence'][entry] += 1 # one cycle for fence instruction
                master_inst_dict[entry] += 1

                # fence clears data cache first as it encounters dirty lines it gives to l2
                # fence clears l2 cache after data cache is cleared
                ops_dict['fence'][entry] += total_cache_line + l2_total_cache_line # each cache line takes one cycle
                master_inst_dict[entry] += total_cache_line + l2_total_cache_line


                dirty_line_index=1 # used to get the next dirty line
                for cache_line in l2_dirty_lines:
                    if (cache_line + cycle_accurate_config['cycles']['bus_latency']['data'] + (number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'])) > total_cache_line:
                        # to see if last few lines are dirty , and add cycles accordingly 
                        master_inst_dict[entry] += (cache_line + cycle_accurate_config['cycles']['bus_latency']['data'] + (number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'])) - total_cache_line
                    if (dirty_line_index < len(l2_dirty_lines)) and ((l2_dirty_lines[dirty_line_index] - cache_line) < number_of_words_in_line): 
                        # to see if there is a gap between dirty lines are less than the number of words in a line(structural hazard)
                        ops_dict['fence'][entry] += (number_of_words_in_line ) - (l2_dirty_lines[dirty_line_index] - cache_line)
                        master_inst_dict[entry] += (number_of_words_in_line ) - (l2_dirty_lines[dirty_line_index] - cache_line)
                    dirty_line_index=dirty_line_index+1

            # sort of creating afresh cache, as fence instruction invalidates the cache
            dl1_miss += d_l1.backend.MISS_count 
            l2_miss += l2.backend.MISS_count

            dl1_hit += d_l1.backend.HIT_count
            l2_hit += l2.backend.HIT_count
            cs.force_write_back('l2')
            cs.force_write_back('d_l1')
            cs.mark_all_invalid('d_l1')
            cs1.mark_all_invalid('l2')
            prev_hits = d_l1.backend.HIT_count
            prev_misses = d_l1.backend.MISS_count
            
            # clearing the dirty lines set as cache is empty after fence instruction
            dirty_lines_set.clear()

        # print (get_backend(l2))
        

        # Handle load/store instructions
        if entry in ops_dict['loads'] or entry in ops_dict['stores']:
                
            # Determine the address based on instruction type
            if 'sp' in entry.instr_name:
                # taking value from x2 as it infers the stack pointer
                base = int(consts.reg_file['x2'], 16)
            else:
                rs = str(entry.rs1[1]) + str(entry.rs1[0]) # gives the register name which is used as base address
                base = int(consts.reg_file.get(rs, consts.freg_file.get(rs, '0x0')), 16)
                    
            # check if immediate value is present
            if entry.imm is None:
                address = base
            else:
                address = base + entry.imm

            last_mem_line_no = line_num

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
            if entry in ops_dict['loads']  :
                if (entry.instr_addr >= cacheable_instr_start and entry.instr_addr <= cacheable_instr_end) and (address >= cacheable_data_start and address <= cacheable_data_end):
                    # checking if the address is in cacheable range
                    cs.load(address, byte_length)
                    if cycle_accurate_config != None:
                        if prev_misses < d_l1.backend.MISS_count:
                            # checking if it's a miss, d_l1.backend.MISS_count is incremented after a load only when it's a miss
                            ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                            master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                            stage2_dict[line_num] = master_inst_dict[entry]

                            # l2 cache checking

                            if l2_prev_misses < l2.backend.MISS_count:
                                additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['miss']
                                l2_prev_misses = l2.backend.MISS_count
                            elif l2_prev_hits < l2.backend.HIT_count:
                                additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['hit']
                                l2_prev_hits = l2.backend.HIT_count
                            ops_dict['loads'][entry] += additional_l2_cycle
                            master_inst_dict[entry] += additional_l2_cycle
                            stage2_dict[line_num] = master_inst_dict[entry]



                        elif prev_hits < d_l1.backend.HIT_count:
                            # checking if it's a hit, d_l1.backend.HIT_count is incremented after a load only when it's a hit
                            ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                            master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                            stage2_dict[line_num] = master_inst_dict[entry]

                else:
                    if cycle_accurate_config != None:
                        # all non cacheable address access is a miss
                        ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                        master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                    

            elif entry in ops_dict['stores'] :
                if(entry.instr_addr >= cacheable_instr_start and entry.instr_addr <= cacheable_instr_end) and (address >= cacheable_data_start and address <= cacheable_data_end):
                    # checking if the address is in cacheable range
                    cs.store(address, byte_length)
                    
                    if cycle_accurate_config != None:
                        if prev_misses < d_l1.backend.MISS_count:

                            # checking if it's a miss, d_l1.backend.MISS_count is incremented after a store only when it's a miss
                            ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                            master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                            stage2_dict[line_num] = master_inst_dict[entry]

                            if l2_prev_misses < l2.backend.MISS_count:
                                additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['miss']
                                l2_prev_misses = l2.backend.MISS_count
                            elif l2_prev_hits < l2.backend.HIT_count:
                                additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['hit']
                                l2_prev_hits = l2.backend.HIT_count
                            ops_dict['stores'][entry] += additional_l2_cycle
                            master_inst_dict[entry] += additional_l2_cycle
                            stage2_dict[line_num] = master_inst_dict[entry]



                        elif prev_hits <= d_l1.backend.HIT_count:
                            # checking if it's a hit, d_l1.backend.HIT_count is incremented or remains same after a store only when it's a hit
                            ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                            master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                            stage2_dict[line_num] = master_inst_dict[entry]

                else:
                    if cycle_accurate_config != None:
                        # all non cacheable address access is a miss
                        ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                        master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
            
            
            
            # keeping track of previous hits and misses, used for knowing the current address is a hit or a miss
            prev_hits = d_l1.backend.HIT_count 
            prev_misses = d_l1.backend.MISS_count


        # Handle register commits
        if entry.reg_commit and entry.reg_commit[1] != '0':
            consts.reg_file[f'x{int(entry.reg_commit[1])}'] = entry.reg_commit[2] 


        # Handle fence instructions
        if 'fence.i' in entry.instr_name:
            il1_miss += i_l1.backend.MISS_count
            il1_hit += i_l1.backend.HIT_count
            instr_invalid_entries = cs1.count_invalid_entries('i_l1')
            instr_temp_total_util = ((total_cache_line - instr_invalid_entries) / total_cache_line) * 100
            cache_util_list1.append(instr_temp_total_util)
            if instr_temp_total_util > total_util1:
                total_util1 = instr_temp_total_util

            # fence.i clears instruction cache
            master_inst_dict[entry] += total_cache_line1
            # invalidating the cache and flushing the pipeline
            # invalidation happens in IF stage and flushing happens in WB stage
            cs1.mark_all_invalid('i_l1')

            
        # Determine the byte length for the operation
        if 'c.' in entry.instr_name:
            # compressed instructions are 2 bytes
            byte_length1 = 2
        else:
            # all other instructions are 4 bytes
            byte_length1 = 4

        # line_num += 1
        stage1_dict[line_num] = 0 # to keep track of stage1 cycles

        # straddle check variables, stradde delay gives extra cycles when straddele occurs
        straddle_check_hit1 = straddle_check_miss1 = straddle_delay1 = 0 

        # Load instruction address into the cache
        if (entry.instr_addr >= cacheable_start1 and entry.instr_addr <= cacheable_end1):
            # checking if the instruction address is in cacheable range
            
            cs1.load(entry.instr_addr, byte_length1)

            if cycle_accurate_config != None:
            
                if prev_hits1 < i_l1.backend.HIT_count:
                    # checking if it's a hit, d_l1.backend.HIT_count is incremented after a load only when it's a hit
                    fetch_cycle1 = cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['hit']
                    # when straddle occurs, and it's a hit then it's a hit in two cache lines. Therefore straddle_check_hit get's incremented by 2
                    # There might be a sdraddle miss then it's a hit on one cahce line and miss on another cache line. Therefore straddle_check_hit get's incremented by 1
                    straddle_check_hit1 = i_l1.backend.HIT_count - prev_hits1
                    # keeping track of previous hits, used for knowing the current address is a hit or a miss
                    prev_hits1 = i_l1.backend.HIT_count  

                # replaced elif with if because of cache line straddling
                if prev_misses1 < i_l1.backend.MISS_count:
                    # checking if it's a miss, d_l1.backend.MISS_count is incremented after a load only when it's a miss
                    fetch_cycle1 = cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['miss']
                    # when straddle occurs, and it's a miss then it's a miss in two cache lines. Therefore straddle_check_miss get's incremented by 2
                    # There might be a sdraddle hit then it's a miss on one cahce line and hit on another cache line. Therefore straddle_check_miss get's incremented by 1
                    straddle_check_miss1 += i_l1.backend.MISS_count - prev_misses1


                    # l2 cache checking
                    if l2_prev_misses < l2.backend.MISS_count:
                        additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['miss']
                        l2_prev_misses = l2.backend.MISS_count
                    elif l2_prev_hits < l2.backend.HIT_count:
                        additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['hit']
                        l2_prev_hits = l2.backend.HIT_count
                    fetch_cycle1 += additional_l2_cycle


                    # keeping track of previous misses, used for knowing the current address is a hit or a miss
                    prev_misses1 = i_l1.backend.MISS_count

                if straddle_check_hit1 == 1 and straddle_check_miss1 == 1:
                    # its straddle and a miss on one line and hit on another line
                    straddle_delay1 = 2 # delay for the above case
                    fetch_cycle1 = fetch_cycle1 + 2
                elif straddle_check_hit1 == 2 and straddle_check_miss1 == 0:
                    # its straddle and a hit on both lines
                    straddle_delay1 = 1 # delay for the above case
                    fetch_cycle1 = fetch_cycle1 + 1
                elif straddle_check_hit1 == 0 and straddle_check_miss1 == 2: # not sure about this case
                    # its straddle and a miss on both lines
                    straddle_delay1 = 1 
                    fetch_cycle1 = fetch_cycle1 + cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['miss'] + 1

                stage1_dict[line_num] = fetch_cycle1 
        else:
            if cycle_accurate_config != None:
                # all non cacheable pc address access is a miss
                fetch_cycle1 = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['instruction']['miss']
            
        if cycle_accurate_config != None:
            if (fetch_cycle1 - prev_last_stage_cycle1) > 0 :
                # checking if fetching of instruction ahs to be stalled
                # if prev_last_stage_cycle1 is greater, then fetch will be completed as previous stage is completed
                for op in ops_dict.keys():
                    if entry in ops_dict[op]:
                    
                        ops_dict[op][entry] = ops_dict[op][entry] + (fetch_cycle1 - prev_last_stage_cycle1)
                        master_inst_dict[entry] = master_inst_dict[entry] + (fetch_cycle1 - prev_last_stage_cycle1)
                        stage1_dict[line_num] = fetch_cycle1 - prev_last_stage_cycle1

                        if line_num in miss_address_dict:
                            miss_address_dict[line_num] = master_inst_dict[entry]


                        # stage2_dict[line_num] = master_inst_dict[entry] - stage1_dict[line_num]
                        prev_last_stage_cycle1 = master_inst_dict[entry] - stage1_dict[line_num]
            else:
                prev_last_stage_cycle1 = master_inst_dict[entry]


    data_invalid_entries = cs.count_invalid_entries('d_l1')
    data_temp_total_util = ((total_cache_line - data_invalid_entries) / total_cache_line) * 100
    cache_util_list.append(data_temp_total_util)
    if data_temp_total_util > total_util:
        total_util = data_temp_total_util  

    # Calculate total utilization percentages
    instr_invalid_entries = cs1.count_invalid_entries('i_l1')
    instr_temp_total_util = ((total_cache_line - instr_invalid_entries) / total_cache_line) * 100
    cache_util_list1.append(instr_temp_total_util)
    if instr_temp_total_util > total_util1:
        total_util1 = instr_temp_total_util

    l2_invalid_lines = cs.count_invalid_entries('l2')
    temp_l2_util = ((l2_total_cache_line - l2_invalid_lines) / l2_total_cache_line)* 100
    cache_util_list2.append(temp_l2_util)
    if temp_l2_util > l2_total_util:
        l2_total_util = temp_l2_util


    dl1_miss+=d_l1.backend.MISS_count
    il1_miss+=i_l1.backend.MISS_count
    l2_miss+=l2.backend.MISS_count

    dl1_hit+=d_l1.backend.HIT_count
    il1_hit+=i_l1.backend.HIT_count
    l2_hit+=l2.backend.HIT_count

    # Update cache utilization information
    cache_dict1['instr_l1']['max utilization(%)'] = total_util1
    cache_dict1['instr_l1']['avg utilization'] = sum(cache_util_list1)/len(cache_util_list1)
    ret_dict_i['Instr cache Maximum Utilization(%)'] = [cache_dict1['instr_l1']['max utilization(%)']]
    ret_dict_i['Instr cache Average Utilization'] = [cache_dict1['instr_l1']['avg utilization']]
    ret_dict_i['Miss Rate'] = [il1_miss/(il1_miss+il1_hit)*100]
    ret_dict_i['Hit Rate'] = [il1_hit/(il1_miss+il1_hit)*100]


    # Update cache utilization information
    cache_dict['data_d_l1']['max utilization(%)'] = total_util
    cache_dict['data_d_l1']['avg utilization'] = sum(cache_util_list)/len(cache_util_list)
    ret_dict_d['Data cache Maximum Utilization(%)'] = [cache_dict['data_d_l1']['max utilization(%)']]
    ret_dict_d['Data cache Average Utilization'] = [cache_dict['data_d_l1']['avg utilization']]
    ret_dict_d['Miss Rate'] = [dl1_miss/(dl1_miss+dl1_hit)*100]
    ret_dict_d['Hit Rate'] = [dl1_hit/(dl1_miss+dl1_hit)*100]

    # update cache utilization information
    cache_dictl2['l2']['max utilization(%)'] = l2_total_util
    cache_dictl2['l2']['avg utilization'] = sum(cache_util_list2)/len(cache_util_list2)
    ret_dict2['L2 cache Maximum Utilization(%)'] = [cache_dictl2['l2']['max utilization(%)']]
    ret_dict2['L2 cache Average Utilization'] = [cache_dictl2['l2']['avg utilization']]
    ret_dict2['Miss Rate'] = [l2_miss/(l2_miss+l2_hit)*100]
    ret_dict2['Hit Rate'] = [l2_hit/(l2_miss+l2_hit)*100]

    # Reset registers
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}

    ret_dict = {}
    ret_dict.update(ret_dict_d)
    ret_dict.update(ret_dict_i)
    ret_dict.update(ret_dict2)

    logger.info("Done.")

    # Return the final results
    return ret_dict




# # Unified computation of instruction and data cache
# # redundant if data and instruction cache are computed separately

# def L1_cache_simulator(master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
#     '''
#     Cycle accurate YAML configuration file is required for this function!!

#     Cache simulator for data cache.
#     Args:
#         - master_inst_dict: A dictionary of InstructionEntry objects.
#         - op_dict: A dictionary with the operations as keys and a list of
#             InstructionEntry objects as values.
#         - extension_used: A list of extensions used in the application.
#         - config: A yaml with the configuration information.
#         - cycle_accurate_config: A dyaml with the cycle accurate configuration information.
        
#         Returns:
#             - A dictionary with the cache level as keys and a list of cache utilization information as values.
#         '''
#     # Logging cache statistics
#     logger.info("Computing Data and Instruction Cache Statistics.") 
    
#     if cycle_accurate_config == None:
#         logger.error("Cycle accurate configuration is missing. Please provide a valid cycle accurate configuration.")
#         return None

#     # List of cache levels
#     cache_list = ['Level 1']

#     # Dictionary to store cache utilization information
#     cache_dict = {"data_d_l1": {'max utilization(%)': 0, "avg utilization": 0} }

#     total_util = 0
#     total_util1 = 0
#     cache_util_list = []

#     # Dictionary to store the final results
#     ret_dict = {'Data Cache': ['Level 1'], 'Data cache Maximum Utilization(%)': [], 'Data cache Average Utilization': [], 'Hit rate': [], 'Miss rate': []}
    
#     d_hit_count = d_miss_count = 0


#     no_of_sets = config['profiles']['cfg']['data_cache']['no_of_sets']
#     no_of_ways = config['profiles']['cfg']['data_cache']['no_of_ways']
#     line_size = config['profiles']['cfg']['data_cache']['line_size']
#     data_cache_replacement_policy = config['profiles']['cfg']['data_cache']['replacement_policy']
#     total_cache_line = no_of_sets * no_of_ways
#     number_of_words_in_line = line_size//4 # line size in byptes / 4 bytes (word size)

#    # Creating the L1 cache
#     mem = MainMemory()
#     d_l1 = Cache("d_l1", no_of_sets, no_of_ways, line_size, data_cache_replacement_policy)
#     mem.load_to(d_l1)
#     mem.store_from(d_l1)
#     cs = CacheSimulator(d_l1, mem)

#     # mem,cs,d_l1 = cache_config.data_cache_configuration("d_l1", None, config)

#     additional_cycle = 0
#     prev_hits = d_l1.backend.HIT_count

#     prev_misses = d_l1.backend.MISS_count

#     cacheable_data_start = int(config['profiles']['cfg']['data_cache']['range']['start'])
#     cacheable_data_end = int(config['profiles']['cfg']['data_cache']['range']['end'])
#     cacheable_instr_start = int(config['profiles']['cfg']['instr_cache']['range']['start'])
#     cacheable_instr_end = int(config['profiles']['cfg']['instr_cache']['range']['end'])

#     hit_address_line_num = miss_address_line_num = 0
#     last_mem_line_no = 0
#     mem_mem_delay = 0
    
#     dirty_lines_set = set() # to keep track of dirty lines
#     line_num = 0 # to keep track of instruction/line number



#     logger.info("Instruction Cache Statistics:")

#     # Setting up memory and cache parameters
#     no_of_sets1 = config['profiles']['cfg']['instr_cache']['no_of_sets']
#     no_of_ways1 = config['profiles']['cfg']['instr_cache']['no_of_ways']
#     line_size1 = config['profiles']['cfg']['instr_cache']['line_size']
#     total_cache_line1 = no_of_sets1 * no_of_ways1
#     instr_cache_replacement_policy = config['profiles']['cfg']['instr_cache']['replacement_policy']
#     number_of_words_in_line1 = line_size1//4 # line size in byptes / 4 bytes (word size)


#     # List of cache levels and dictionary to store cache utilization information
#     cache_list1 = ['Level 1']
#     cache_dict1 = {"instr_d_l1": {'max utilization(%)': 0, "avg utilization": 0} }


#     total_util1 = 0
#     cache_util_list1 = []

#     # Dictionary to store the final results
#     ret_dict1 = {'Instruction Cache': ['Level 1'], 'Instr cache Maximum Utilization(%)': [], 'Instr cache Average Utilization': [], 'Hit rate': [], 'Miss rate': []}

#     i_hit_count = i_miss_count = 0
    
#     i_l1 = Cache("i_l1", no_of_sets1, no_of_ways1, line_size1, instr_cache_replacement_policy)
#     cs1 = CacheSimulator(i_l1, mem)

#     # cs1,i_l1 = cache_config.instruction_cache_configuration("i_l1", None, config)



#     # Loop through master instruction list
#     prev_hits1 = i_l1.backend.HIT_count
#     prev_misses1 = i_l1.backend.MISS_count
#     prev_last_stage_cycle1 = 0
#     fetch_cycle1 = 0
#     cacheable_start1 = int(config['profiles']['cfg']['instr_cache']['range']['start'])
#     cacheable_end1 = int(config['profiles']['cfg']['instr_cache']['range']['end'])
#     # keeping track of instruction/line number
#     # line_num = 0
#     keys_to_delete1 = {}
#     # print(data_cache_status)




#     # Loop through instructions
#     for entry in master_inst_dict:
#         line_num += 1 
#         if 'fence' in entry.instr_name:
            
#             # computing cache utilization 
#             data_invalid_entries = cs.count_invalid_entries('d_l1')
#             data_temp_total_util = ((total_cache_line - data_invalid_entries) / total_cache_line) * 100
#             cache_util_list.append(data_temp_total_util)
#             if data_temp_total_util > total_util:
#                 total_util = data_temp_total_util
#             d_hit_count += d_l1.backend.HIT_count
#             d_miss_count += d_l1.backend.MISS_count

#             dirty_lines_set = cs.dirty_cl_ids('d_l1') # getting dirty lines set
#             # sorting the dirty lines set, as fence instruction traverse the cache in sorted order
#             sorted_dirty_lines_set = tuple(sorted(dirty_lines_set))

#             ops_dict['fence'][entry] += 1 # one cycle for fence instruction
#             master_inst_dict[entry] += 1

#             ops_dict['fence'][entry] += total_cache_line # each cache line takes one cycle
#             master_inst_dict[entry] += total_cache_line

#             dirty_line_index=1 # used to get the next dirty line
#             for cache_line in sorted_dirty_lines_set:
#                 if (cache_line + cycle_accurate_config['cycles']['bus_latency']['data'] + (number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'])) > total_cache_line:
#                     # to see if last few lines are dirty , and add cycles accordingly 
#                     master_inst_dict[entry] += (cache_line + cycle_accurate_config['cycles']['bus_latency']['data'] + (number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'])) - total_cache_line
#                 if (dirty_line_index < len(sorted_dirty_lines_set)) and ((sorted_dirty_lines_set[dirty_line_index] - cache_line) < number_of_words_in_line): 
#                     # to see if there is a gap between dirty lines are less than the number of words in a line(structural hazard)
#                     ops_dict['fence'][entry] += (number_of_words_in_line ) - (sorted_dirty_lines_set[dirty_line_index] - cache_line)
#                     master_inst_dict[entry] += (number_of_words_in_line ) - (sorted_dirty_lines_set[dirty_line_index] - cache_line)
#                 dirty_line_index=dirty_line_index+1

#             # sort of creating afresh cache, as fence instruction invalidates the cache
#             cs.force_write_back('d_l1')
#             cs.mark_all_invalid('d_l1')
#             prev_hits = d_l1.backend.HIT_count
#             prev_misses = d_l1.backend.MISS_count
            
#             # clearing the dirty lines set as cache is empty after fence instruction
#             dirty_lines_set.clear()

        

#         # Handle load/store instructions
#         if entry in ops_dict['loads'] or entry in ops_dict['stores']:
                
#             # Determine the address based on instruction type
#             if 'sp' in entry.instr_name:
#                 # taking value from x2 as it infers the stack pointer
#                 base = int(consts.reg_file['x2'], 16)
#             else:
#                 rs = str(entry.rs1[1]) + str(entry.rs1[0]) # gives the register name which is used as base address
#                 base = int(consts.reg_file.get(rs, consts.freg_file.get(rs, '0x0')), 16)
                    
#             # check if immediate value is present
#             if entry.imm is None:
#                 address = base
#             else:
#                 address = base + entry.imm

#             last_mem_line_no = line_num

#             # Determine the byte length for the operation
#             if ('d' in entry.instr_name):
#                 byte_length = 8
#             elif ('w' in entry.instr_name):
#                 byte_length = 4
#             elif ('h' in entry.instr_name):
#                 byte_length = 2
#             elif ('b' in entry.instr_name):
#                 byte_length = 1
#             # Handle load and store operations
#             if entry in ops_dict['loads']  :
#                 if (entry.instr_addr >= cacheable_instr_start and entry.instr_addr <= cacheable_instr_end) and (address >= cacheable_data_start and address <= cacheable_data_end):
#                     # checking if the address is in cacheable range
#                     cs.load(address, byte_length)
#                     # checking if it's a miss, d_l1.backend.MISS_count is incremented after a load only when it's a miss
#                     if prev_misses < d_l1.backend.MISS_count:
#                         # miss latency alloted
#                         ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
#                         master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
#                         stage2_dict[line_num] = master_inst_dict[entry]

#                         # since data cache is partial critical workd first, we need to see if previous miss is still busy filling the cache line
#                         # if it's busy then we need to add cycles to the current instruction
#                         if line_num - miss_address_line_num > 0 and miss_address_line_num != 0:
#                             if (line_num - miss_address_line_num) < number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache']:
#                                 for add_len in range(0,line_num - miss_address_line_num,cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
#                                     # keeping track of how many instructions will data cache be busy in case it's a miss, considering each fill takes one cycle
#                                     data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
#                                 master_inst_dict[entry] = master_inst_dict[entry] + (number_of_words_in_line - (line_num - miss_address_line_num))
#                                 ops_dict['loads'][entry] = ops_dict['loads'][entry] + (number_of_words_in_line - (line_num - miss_address_line_num))
#                                 mem_mem_dict[line_num] = (number_of_words_in_line - (line_num - miss_address_line_num))

#                         miss_address_line_num = line_num # keeping track of the instruction number which caused a miss

#                         data_cache_status[line_num] = number_of_words_in_line

#                         # keeping track of instructions that cused a data cache miss and the instruction number
#                         miss_address_dict[line_num] = entry



#                     elif prev_hits < d_l1.backend.HIT_count:
#                         # checking if it's a hit, d_l1.backend.HIT_count is incremented after a load only when it's a hit
#                         ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
#                         master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
#                         stage2_dict[line_num] = master_inst_dict[entry]

#                         hit_address_line_num = line_num
#                         if hit_address_line_num - miss_address_line_num > 0 and miss_address_line_num != 0:
#                             # data cache will complete writing in the instruction causes a hit in the data cache
#                             if (hit_address_line_num - miss_address_line_num) < number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache']:
#                                 for add_len in range(0,hit_address_line_num - miss_address_line_num,cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
#                                     # keeping track of how many instructions will data cache be busy in case it's a miss, considering each fill takes one cycle
#                                     data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
#                                 master_inst_dict[entry] = master_inst_dict[entry] + (number_of_words_in_line - (hit_address_line_num - miss_address_line_num))
#                                 ops_dict['loads'][entry] = ops_dict['loads'][entry] + (number_of_words_in_line - (hit_address_line_num - miss_address_line_num))
#                                 mem_mem_dict[line_num] = (number_of_words_in_line - (hit_address_line_num - miss_address_line_num))
#                             else:
#                                 for add_len in range(0,number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'],cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
#                                     # keeping track of how many instructions will data cache be busy in case it's a miss, considering each fill takes one cycle
#                                     data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
#                             miss_address_line_num = 0

#                 else:
#                     # all non cacheable address access is a miss
#                     ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
#                     master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                    

#             elif entry in ops_dict['stores'] :
#                 if(entry.instr_addr >= cacheable_instr_start and entry.instr_addr <= cacheable_instr_end) and (address >= cacheable_data_start and address <= cacheable_data_end):
#                     # checking if the address is in cacheable range\
#                     cs.store(address, byte_length)

#                     if prev_misses < d_l1.backend.MISS_count:

#                         # checking if it's a miss, d_l1.backend.MISS_count is incremented after a store only when it's a miss
#                         ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
#                         master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
#                         stage2_dict[line_num] = master_inst_dict[entry]

#                         if line_num - miss_address_line_num > 0 and miss_address_line_num != 0:
#                             if (line_num - miss_address_line_num) < number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache']:
#                                 for add_len in range(0,line_num - miss_address_line_num,cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
#                                     # keeping track of how many instructions will data cache be busy in cse it's a miss, considering each fill takes one cycle
#                                     data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
#                                 master_inst_dict[entry] = master_inst_dict[entry] + (number_of_words_in_line - (line_num - miss_address_line_num))
#                                 ops_dict['stores'][entry] = ops_dict['stores'][entry] + (number_of_words_in_line - (line_num - miss_address_line_num))
#                                 mem_mem_dict[line_num] = (number_of_words_in_line - (line_num - miss_address_line_num))

#                         miss_address_line_num = line_num

#                         data_cache_status[line_num] = number_of_words_in_line

#                         # keeping track of instructions that cused a data cache miss and the instruction number
#                         miss_address_dict[line_num] = entry



#                     elif prev_hits <= d_l1.backend.HIT_count:
#                         # checking if it's a hit, d_l1.backend.HIT_count is incremented or remains same after a store only when it's a hit
#                         ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
#                         master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
#                         stage2_dict[line_num] = master_inst_dict[entry]
#                         hit_address_line_num = line_num
#                         if hit_address_line_num - miss_address_line_num > 0 and miss_address_line_num != 0:
#                             # data cache will complete writing in the instruction causes a hit in the data cache
#                             if (hit_address_line_num - miss_address_line_num) < number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache']:
#                                 for add_len in range(0,hit_address_line_num - miss_address_line_num,cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
#                                     # keeping track of how many instructions will data cache be busy in cse it's a miss, considering each fill takes one cycle
#                                     data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
#                                 master_inst_dict[entry] = master_inst_dict[entry] + (number_of_words_in_line - (hit_address_line_num - miss_address_line_num))
#                                 ops_dict['stores'][entry] = ops_dict['stores'][entry] + (number_of_words_in_line - (hit_address_line_num - miss_address_line_num)) 
#                                 mem_mem_dict[line_num] = (number_of_words_in_line - (hit_address_line_num - miss_address_line_num))
#                             else:
#                                 for add_len in range(0,number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'],cycle_accurate_config['cycles']['structural_hazards']['data_cache']):
#                                     # keeping track of how many instructions will data cache be busy in cse it's a miss, considering each fill takes one cycle
#                                     data_cache_status[miss_address_line_num+add_len] = number_of_words_in_line - add_len
#                             miss_address_line_num = 0

#                 else:
#                     # all non cacheable address access is a miss
#                     ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
#                     master_inst_dict[entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
            
            
            
#             # keeping track of previous hits and misses, used for knowing the current address is a hit or a miss
#             prev_hits = d_l1.backend.HIT_count 
#             prev_misses = d_l1.backend.MISS_count


#         # Handle register commits
#         if entry.reg_commit and entry.reg_commit[1] != '0':
#             consts.reg_file[f'x{int(entry.reg_commit[1])}'] = entry.reg_commit[2] 




#         # Handle fence instructions
#         if 'fence.i' in entry.instr_name:
#             instr_invalid_entries = cs1.count_invalid_entries('i_l1')
#             instr_temp_total_util = ((total_cache_line - instr_invalid_entries) / total_cache_line) * 100
#             cache_util_list1.append(instr_temp_total_util)
#             if instr_temp_total_util > total_util1:
#                 total_util1 = instr_temp_total_util
            
#             # flush i cache
#             master_inst_dict[entry] += total_cache_line1

#             i_hit_count += i_l1.backend.HIT_count
#             i_miss_count += i_l1.backend.MISS_count
#             # invalidating the cache and flushing the pipeline
#             # invalidation happens in IF stage and flushing happens in WB stage
#             cs1.mark_all_invalid('i_l1')
            
#         # Determine the byte length for the operation
#         if 'c.' in entry.instr_name:
#             # compressed instructions are 2 bytes
#             byte_length1 = 2
#         else:
#             # all other instructions are 4 bytes
#             byte_length1 = 4

#         # line_num += 1
#         stage1_dict[line_num] = 0 # to keep track of stage1 cycles

#         # straddle check variables, stradde delay gives extra cycles when straddele occurs
#         straddle_check_hit1 = straddle_check_miss1 = straddle_delay1 = 0 

#         # Load instruction address into the cache
#         if (entry.instr_addr >= cacheable_start1 and entry.instr_addr <= cacheable_end1):
#             # checking if the instruction address is in cacheable range
            
#             cs1.load(entry.instr_addr, byte_length1)
            
#             if prev_hits1 < i_l1.backend.HIT_count:
#                 # checking if it's a hit, d_l1.backend.HIT_count is incremented after a load only when it's a hit
#                 fetch_cycle1 = cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['hit']
#                 # when straddle occurs, and it's a hit then it's a hit in two cache lines. Therefore straddle_check_hit get's incremented by 2
#                 # There might be a sdraddle miss then it's a hit on one cahce line and miss on another cache line. Therefore straddle_check_hit get's incremented by 1
#                 straddle_check_hit1 = i_l1.backend.HIT_count - prev_hits1
#                 # keeping track of previous hits, used for knowing the current address is a hit or a miss
#                 prev_hits1 = i_l1.backend.HIT_count  

#             # replaced elif with if because of cache line straddling
#             if prev_misses1 < i_l1.backend.MISS_count:
#                 # checking if it's a miss, d_l1.backend.MISS_count is incremented after a load only when it's a miss
#                 fetch_cycle1 = cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['miss']
#                 # when straddle occurs, and it's a miss then it's a miss in two cache lines. Therefore straddle_check_miss get's incremented by 2
#                 # There might be a sdraddle hit then it's a miss on one cahce line and hit on another cache line. Therefore straddle_check_miss get's incremented by 1
#                 straddle_check_miss1 += i_l1.backend.MISS_count - prev_misses1
#                 # keeping track of previous misses, used for knowing the current address is a hit or a miss
#                 prev_misses1 = i_l1.backend.MISS_count

#             if straddle_check_hit1 == 1 and straddle_check_miss1 == 1:
#                 # its straddle and a miss on one line and hit on another line
#                 straddle_delay1 = 2 # delay for the above case
#                 fetch_cycle1 = fetch_cycle1 + 2
#             elif straddle_check_hit1 == 2 and straddle_check_miss1 == 0:
#                 # its straddle and a hit on both lines
#                 straddle_delay1 = 1 # delay for the above case
#                 fetch_cycle1 = fetch_cycle1 + 1
#             elif straddle_check_hit1 == 0 and straddle_check_miss1 == 2: # not sure about this case
#                 # its straddle and a miss on both lines
#                 straddle_delay1 = 1 
#                 fetch_cycle1 = fetch_cycle1 + cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['miss'] + 1

#             stage1_dict[line_num] = fetch_cycle1 
#         else:
#             # all non cacheable pc address access is a miss
#             fetch_cycle1 = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['instruction']['miss']
            
#         # fetching and filling of cache can be done parallely, 
#         # if current instr is a cache miss and and the bus is still busy filling the data cache 
#         # then we finish filling the data the cache fully as we do instr fetch
#         # so the instr which were busy filling the data cache shpuld be removed from data cache status
#         if line_num in data_cache_status:
#             if fetch_cycle1 > (data_cache_status[line_num]):
#                 i=0
#                 if data_cache_status[line_num] >= number_of_words_in_line1 - 1 and (line_num - 1) in data_cache_status:
#                     keys_to_delete1[line_num] = data_cache_status[line_num - 1] - 1
#                 elif data_cache_status[line_num] < number_of_words_in_line1 :
#                     keys_to_delete1[line_num] = data_cache_status[line_num]
#                 for i in range(1, data_cache_status[line_num]):
#                     if (line_num + i) in data_cache_status:
#                         if data_cache_status[line_num + i] >= data_cache_status[line_num]:
#                             break
#                         else:
#                             # keys_to_delete[line_num + i] = data_cache_status[line_num + i]
#                             continue
#                 if (line_num + i - 1) in data_cache_status:
#                     keys_to_delete1[line_num + i] = data_cache_status[line_num + i - 1] - 1

#                 # print(keys_to_delete)
        
#         if line_num in keys_to_delete1:
#             if line_num in mem_mem_dict:
#                 master_inst_dict[entry] = master_inst_dict[entry] - keys_to_delete1[line_num]
#             elif keys_to_delete1[line_num] > cycle_accurate_config['cycles']['mem_latency']['cacheable']['instruction']['hit']:
#                 master_inst_dict[entry] = master_inst_dict[entry] + keys_to_delete1[line_num] 

#         # checking if fetch cycle is greater than previous last stage cycle

#         if (fetch_cycle1 - prev_last_stage_cycle1) > 0 :
#             # checking if fetching of instruction ahs to be stalled
#             # if prev_last_stage_cycle1 is greater, then fetch will be completed as previous stage is completed
#             for op in ops_dict.keys():
#                 if entry in ops_dict[op]:
                
#                     ops_dict[op][entry] = ops_dict[op][entry] + (fetch_cycle1 - prev_last_stage_cycle1)
#                     master_inst_dict[entry] = master_inst_dict[entry] + (fetch_cycle1 - prev_last_stage_cycle1)
#                     stage1_dict[line_num] = fetch_cycle1 - prev_last_stage_cycle1

#                     if line_num in miss_address_dict:
#                         miss_address_dict[line_num] = master_inst_dict[entry]


#                     # stage2_dict[line_num] = master_inst_dict[entry] - stage1_dict[line_num]
#                     prev_last_stage_cycle1 = master_inst_dict[entry] - stage1_dict[line_num]
#         else:
#             prev_last_stage_cycle1 = master_inst_dict[entry]

#     instr_invalid_entries = cs1.count_invalid_entries('i_l1')
#     instr_temp_total_util = ((total_cache_line - instr_invalid_entries) / total_cache_line) * 100
#     cache_util_list1.append(instr_temp_total_util)
#     if instr_temp_total_util > total_util1:
#         total_util1 = instr_temp_total_util
#     i_hit_count += i_l1.backend.HIT_count
#     i_miss_count += i_l1.backend.MISS_count
#     # Update cache utilization information
#     cache_dict1['instr_d_l1']['max utilization(%)'] = total_util1
#     cache_dict1['instr_d_l1']['avg utilization'] = sum(cache_util_list1)/len(cache_util_list1)
#     ret_dict1['Instr cache Maximum Utilization(%)'] = [cache_dict1['instr_d_l1']['max utilization(%)']]
#     ret_dict1['Instr cache Average Utilization'] = [cache_dict1['instr_d_l1']['avg utilization']]
#     ret_dict1['Hit rate'] = [(i_hit_count/(i_hit_count+i_miss_count))*100]
#     ret_dict1['Miss rate'] = [(i_miss_count/(i_hit_count+i_miss_count))*100]

#     data_invalid_entries = cs.count_invalid_entries('d_l1')
#     data_temp_total_util = ((total_cache_line - data_invalid_entries) / total_cache_line) * 100
#     cache_util_list.append(data_temp_total_util)
#     if data_temp_total_util > total_util:
#         total_util = data_temp_total_util
#     d_hit_count += d_l1.backend.HIT_count
#     d_miss_count += d_l1.backend.MISS_count
#     # Update cache utilization information
#     cache_dict['data_d_l1']['max utilization(%)'] = total_util
#     cache_dict['data_d_l1']['avg utilization'] = sum(cache_util_list)/len(cache_util_list)
#     ret_dict['Data cache Maximum Utilization(%)'] = [cache_dict['data_d_l1']['max utilization(%)']]
#     ret_dict['Data cache Average Utilization'] = [cache_dict['data_d_l1']['avg utilization']]
#     ret_dict['Hit rate'] = [(d_hit_count/(d_hit_count+d_miss_count))*100]
#     ret_dict['Miss rate'] = [(d_miss_count/(d_hit_count+d_miss_count))*100]

#     # Reset registers
#     consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}

#     logger.info("Done")

#     # Return the final results
#     ret_dict.update(ret_dict1)
#     return ret_dict
