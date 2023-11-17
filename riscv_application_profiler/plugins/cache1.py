from cachesim import CacheSimulator, Cache, MainMemory, CacheVisualizer, get_backend
import riscv_application_profiler.consts as consts
from riscv_isac.log import *
import riscv_application_profiler.plugins.cache_config as cache_config

miss_address_dict = dict()
hit_address_dict = dict()
miss_inst_dict = dict()
stage2_dict = dict()
stage1_dict = dict()
data_cache_status = dict()
mem_mem_dict = dict()
setup = list()

def cache_setup (cache,config):
    if setup == []:
        mem,D_cs,I_cs,D_cache_level,I_cache_level = cache_config.d_l1_config("l1", config)
        setup.append(1)
    if cache == 'data':
        return mem,D_cs,D_cache_level
    elif cache == 'instr':
        return mem,I_cs,I_cache_level

def cache_simulator(master_inst_list: list, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
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
    cache_dict = {"data_d_l1": {'max utilization(%)': 0, "avg utilization": 0} }

    total_util = 0
    total_util1 = 0
    cache_util_list = []

    # Dictionary to store the final results
    ret_dict = {'Data Cache': ['Level 1'], 'Data cache Maximum Utilization(%)': [], 'Data cache Average Utilization': []}
    # mem,cs,d_l1 = cache_setup('data', config)


    no_of_sets = config['profiles']['cfg']['data_cache']['no_of_sets']
    no_of_ways = config['profiles']['cfg']['data_cache']['no_of_ways']
    line_size = config['profiles']['cfg']['data_cache']['line_size']
    dCache_replacement_policy = config['profiles']['cfg']['data_cache']['replacement_policy']
    total_cache_line = no_of_sets * no_of_ways
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
    ret_dict2 = {'L2 Cache': ['Level 2'], 'L2 cache Maximum Utilization(%)': [], 'L2 cache Average Utilization': []}
    cache_util_list2 = []


    d_l1 = Cache("d_l1", no_of_sets, no_of_ways, line_size, dCache_replacement_policy, load_from=l2, store_to=l2)
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
    iCache_replacement_policy = config['profiles']['cfg']['instr_cache']['replacement_policy']
    number_of_words_in_line1 = line_size1//4 # line size in byptes / 4 bytes (word size)


    # List of cache levels and dictionary to store cache utilization information
    cache_list1 = ['Level 1']
    cache_dict1 = {"instr_d_l1": {'max utilization(%)': 0, "avg utilization": 0} }


    total_util1 = 0
    cache_util_list1 = []
    

    # Dictionary to store the final results
    ret_dict1 = {'Instruction Cache': ['Level 1'], 'Instr cache Maximum Utilization(%)': [], 'Instr cache Average Utilization': []}


    
    i_l1 = Cache("i_l1", no_of_sets1, no_of_ways1, line_size1, "LFSR", load_from=l2, store_to=l2)
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
    for entry in master_inst_list:
        line_num += 1 
        if 'fence' in entry.instr_name:
            d_l1_dirty_lines = cs.dirty_cl_ids('d_l1')
            l2_dirty_lines = cs.dirty_cl_ids('l2')


            dl1_miss += d_l1.backend.MISS_count 
            il1_miss += i_l1.backend.MISS_count
            l2_miss += l2.backend.MISS_count

            dl1_hit += d_l1.backend.HIT_count
            il1_hit += i_l1.backend.HIT_count
            l2_hit += l2.backend.HIT_count


            # DEBUG : flush l1 first and then l2

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
            master_inst_list[entry] += 1

            ops_dict['fence'][entry] += total_cache_line + l2_total_cache_line # each cache line takes one cycle
            master_inst_list[entry] += total_cache_line + l2_total_cache_line


            j=1 # used to get the next dirty line
            for cache_line in l2_dirty_lines:
                if (cache_line + cycle_accurate_config['cycles']['bus_latency']['data'] + (number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'])) > total_cache_line:
                    # to see if last few lines are dirty , and add cycles accordingly 
                    master_inst_list[entry] += (cache_line + cycle_accurate_config['cycles']['bus_latency']['data'] + (number_of_words_in_line - cycle_accurate_config['cycles']['structural_hazards']['data_cache'])) - total_cache_line
                if (j < len(l2_dirty_lines)) and ((l2_dirty_lines[j] - cache_line) < number_of_words_in_line): # DEBUG: check if it's less than 8 or 18 and how much delay cycles to add
                    # to see if there is a gap between dirty lines are less than the number of words in a line(structural hazard)
                    ops_dict['fence'][entry] += (number_of_words_in_line ) - (l2_dirty_lines[j] - cache_line)
                    master_inst_list[entry] += (number_of_words_in_line ) - (l2_dirty_lines[j] - cache_line)
                j=j+1

            # sort of creating afresh cache, as fence instruction invalidates the cache
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
                    if prev_misses < d_l1.backend.MISS_count:
                        # checking if it's a miss, d_l1.backend.MISS_count is incremented after a load only when it's a miss
                        ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                        master_inst_list[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                        stage2_dict[line_num] = master_inst_list[entry]

                        # l2 cache checking

                        if l2_prev_misses < l2.backend.MISS_count:
                            additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['miss']
                            l2_prev_misses = l2.backend.MISS_count
                        elif l2_prev_hits < l2.backend.HIT_count:
                            additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['hit']
                            l2_prev_hits = l2.backend.HIT_count
                        ops_dict['loads'][entry] += additional_l2_cycle
                        master_inst_list[entry] += additional_l2_cycle
                        stage2_dict[line_num] = master_inst_list[entry]



                    elif prev_hits < d_l1.backend.HIT_count:
                        # checking if it's a hit, d_l1.backend.HIT_count is incremented after a load only when it's a hit
                        ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                        master_inst_list[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                        stage2_dict[line_num] = master_inst_list[entry]

                else:
                    # all non cacheable address access is a miss
                    ops_dict['loads'][entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                    master_inst_list[entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                    

            elif entry in ops_dict['stores'] :
                if(entry.instr_addr >= cacheable_instr_start and entry.instr_addr <= cacheable_instr_end) and (address >= cacheable_data_start and address <= cacheable_data_end):
                    # checking if the address is in cacheable range\
                    cs.store(address, byte_length)

                    if prev_misses < d_l1.backend.MISS_count:

                        # checking if it's a miss, d_l1.backend.MISS_count is incremented after a store only when it's a miss
                        ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                        master_inst_list[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['miss'] 
                        stage2_dict[line_num] = master_inst_list[entry]

                        if l2_prev_misses < l2.backend.MISS_count:
                            additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['miss']
                            l2_prev_misses = l2.backend.MISS_count
                        elif l2_prev_hits < l2.backend.HIT_count:
                            additional_l2_cycle = cycle_accurate_config['cycles']['mem_latency']['cacheable']['L2']['hit']
                            l2_prev_hits = l2.backend.HIT_count
                        ops_dict['stores'][entry] += additional_l2_cycle
                        master_inst_list[entry] += additional_l2_cycle
                        stage2_dict[line_num] = master_inst_list[entry]



                    elif prev_hits <= d_l1.backend.HIT_count:
                        # checking if it's a hit, d_l1.backend.HIT_count is incremented or remains same after a store only when it's a hit
                        ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                        master_inst_list[entry] = cycle_accurate_config['cycles']['mem_latency']['cacheable']['data']['hit'] 
                        stage2_dict[line_num] = master_inst_list[entry]

                    # calculating the dirty line using cache line id
                    cl_id = address >> cs.last_level.backend.cl_bits
                    set_id = cl_id % no_of_sets
                    way_id = cl_id % no_of_ways
                    dirty_line = (set_id*no_of_ways) + way_id
                    dirty_lines_set.add(dirty_line+1)
                    dirty_cl_id_set.add(cl_id)

                else:
                    # all non cacheable address access is a miss
                    ops_dict['stores'][entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
                    master_inst_list[entry] = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['data']['miss']
            
            
            
            # keeping track of previous hits and misses, used for knowing the current address is a hit or a miss
            prev_hits = d_l1.backend.HIT_count 
            prev_misses = d_l1.backend.MISS_count


        # Handle register commits
        if entry.reg_commit and entry.reg_commit[1] != '0':
            consts.reg_file[f'x{int(entry.reg_commit[1])}'] = entry.reg_commit[2] 


        # Handle fence instructions
        if 'fence.i' in entry.instr_name:
            instr_invalid_entries = cs1.count_invalid_entries('i_l1')
            instr_temp_total_util = ((total_cache_line - instr_invalid_entries) / total_cache_line) * 100
            cache_util_list1.append(instr_temp_total_util)
            if instr_temp_total_util > total_util1:
                total_util1 = instr_temp_total_util
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
            # all non cacheable pc address access is a miss
            fetch_cycle1 = cycle_accurate_config['cycles']['mem_latency']['non_cacheable']['instruction']['miss']
            

        if (fetch_cycle1 - prev_last_stage_cycle1) > 0 :
            # checking if fetching of instruction ahs to be stalled
            # if prev_last_stage_cycle1 is greater, then fetch will be completed as previous stage is completed
            for op in ops_dict.keys():
                if entry in ops_dict[op]:
                
                    ops_dict[op][entry] = ops_dict[op][entry] + (fetch_cycle1 - prev_last_stage_cycle1)
                    master_inst_list[entry] = master_inst_list[entry] + (fetch_cycle1 - prev_last_stage_cycle1)
                    stage1_dict[line_num] = fetch_cycle1 - prev_last_stage_cycle1

                    if line_num in miss_address_dict:
                        miss_address_dict[line_num] = master_inst_list[entry]


                    # stage2_dict[line_num] = master_inst_list[entry] - stage1_dict[line_num]
                    prev_last_stage_cycle1 = master_inst_list[entry] - stage1_dict[line_num]
        else:
            prev_last_stage_cycle1 = master_inst_list[entry]


    # Print cache statistics
    cs.print_stats()
    data_invalid_entries = cs.count_invalid_entries('d_l1')
    data_temp_total_util = ((total_cache_line - data_invalid_entries) / total_cache_line) * 100
    cache_util_list.append(data_temp_total_util)
    if data_temp_total_util > total_util:
        total_util = data_temp_total_util


    cs1.print_stats()


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

    # Update cache utilization information
    cache_dict1['instr_d_l1']['max utilization(%)'] = total_util1
    cache_dict1['instr_d_l1']['avg utilization'] = sum(cache_util_list1)/len(cache_util_list1)
    ret_dict1['Instr cache Maximum Utilization(%)'] = [cache_dict1['instr_d_l1']['max utilization(%)']]
    ret_dict1['Instr cache Average Utilization'] = [cache_dict1['instr_d_l1']['avg utilization']]


    # Update cache utilization information
    cache_dict['data_d_l1']['max utilization(%)'] = total_util
    cache_dict['data_d_l1']['avg utilization'] = sum(cache_util_list)/len(cache_util_list)
    ret_dict['Data cache Maximum Utilization(%)'] = [cache_dict['data_d_l1']['max utilization(%)']]
    ret_dict['Data cache Average Utilization'] = [cache_dict['data_d_l1']['avg utilization']]

    # update cache utilization information
    cache_dict['l2']['max utilization(%)'] = l2_total_util
    cache_dict['l2']['avg utilization'] = sum(cache_util_list2)/len(cache_util_list2)
    ret_dict2['L2 cache Maximum Utilization(%)'] = [cache_dict['l2']['max utilization(%)']]
    ret_dict2['L2 cache Average Utilization'] = [cache_dict['l2']['avg utilization']]

    # Reset registers
    consts.reg_file = {f'x{i}': '0x00000000' for i in range(32)}
    consts.reg_file['x2'] = '0x800030d0'
    consts.reg_file['x3'] = '0x800030d0'

    dl1_miss+=d_l1.backend.MISS_count
    il1_miss+=i_l1.backend.MISS_count
    l2_miss+=l2.backend.MISS_count

    dl1_hit+=d_l1.backend.HIT_count
    il1_hit+=i_l1.backend.HIT_count
    l2_hit+=l2.backend.HIT_count

    print("dl1 miss rate, il1 miss rate, l2 miss rate")
    print((dl1_miss/(dl1_miss+dl1_hit))*100, (il1_miss/(il1_miss+il1_hit))*100, (l2_miss/(l2_miss+l2_hit))*100)

    # Return the final results
    return ret_dict, ret_dict1

