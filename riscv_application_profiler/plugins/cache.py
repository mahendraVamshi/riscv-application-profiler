from cachesim import CacheSimulator, Cache, MainMemory
import riscv_application_profiler.consts as consts
from riscv_isac.log import *
import os
import yaml

script_directory = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '..', 'config.yaml')
with open(config_path, 'r') as config_file:
    config = yaml.safe_load(config_file)

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
    if 'cfg1' in config['profiles']:
        metrics = config['profiles']['cfg1']['metrics']
        if 'cache' in metrics:
            logger.info("Data Cache Statistics:")
    
    load_list=op_dict['loads']
    store_list=op_dict['stores']
    cache_list=['Level 1']
    cache_dict={l:{'utilization(%)':0} for l in cache_list}

    mem = MainMemory()
    no_of_sets=64
    no_of_ways=4
    line_size=64
    l1 = Cache("L1", no_of_sets, no_of_ways, line_size, "RR")  # 64 sets, 4-ways with cacheline size of 64 bytes, replacement policy=Round Robin
    #total cache size=16384 bytes
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)
    min_util=cs.count_invalid_entries()
    max_util=cs.count_invalid_entries()
    for i in master_inst_list:
        if (i.reg_commit is not None):
            consts.reg_file[f'x{i.reg_commit[1]}'] = i.reg_commit[2]
        if (i in load_list or i in store_list):
            if ('sp' in i.instr_name):
                base = int(consts.reg_file['x2'],16)
                if (i.imm is None):
                    address = base
                else:
                    address = base+abs(i.imm)
            else:
                rs1=str(i.rs1[1])+str(i.rs1[0])
                if rs1 in consts.reg_file:
                    base = int(consts.reg_file[rs1],16)
                elif rs1 in consts.freg_file:
                    base = int(consts.freg_file[rs1],16)
                if (i.imm is None):
                    address = base
                else:
                    address = base+i.imm
            if ('d' in i.instr_name):
                byte_length = 8
            elif ('w' in i.instr_name):
                byte_length = 4
            elif ('h' in i.instr_name):
                byte_length = 2
            elif ('b' in i.instr_name):
                byte_length = 1
        if (i in load_list):
            cs.load(address, byte_length)
            
        elif (i in store_list):
            cs.store(address, byte_length)
        
        this_util=cs.count_invalid_entries() 
        if this_util>max_util:
            max_util=this_util
        if this_util<min_util:
            min_util=this_util
    if 'cache' in metrics:
        cs.print_stats()
    max_util=max_util*line_size
    min_util=min_util*line_size

    total_util=((max_util-min_util)/max_util)*100
    cache_dict['Level 1']['utilization(%)']=total_util
    
    # print(f"total_cache_utilization: {total_util:.2f}%")
    
    # total_lines= no_of_sets*no_of_ways
    # unutilized_lines=cs.count_invalid_entries()
    # cache_utilization=((total_lines-unutilized_lines)/total_lines)*100
    # print(f"cache_utilization: {cache_utilization:.2f}%")
    return(cache_list,cache_dict)


def instruction_cache_simulator(master_inst_list):
    '''
    Cache simulator for instruction cache.
    Args:
        - master_inst_list: A list of InstructionEntry objects.
        
        Returns:
            - A list of cache names and a dictionary with the cache names as keys
              and a dictionary with the cache statistics as values.
    
    '''
    if 'cfg1' in config['profiles']:
        metrics = config['profiles']['cfg1']['metrics']
        if 'cache' in metrics:
            logger.info("Instruction Cache Statistics:")
    
    mem = MainMemory()
    cache_list=['Level 1']
    cache_dict={l:{'utilization(%)':0} for l in cache_list}
    no_of_sets=64
    no_of_ways=4
    line_size=64
    l1 = Cache("L1", no_of_sets, no_of_ways, line_size, "LRU")  # 64 sets, 4-ways with cacheline size of 64 bytes, replacement policy=Random
    #total cache size=16384 bytes
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)
    min_util=cs.count_invalid_entries()
    max_util=cs.count_invalid_entries()
    byte_length=4
    for entry in master_inst_list:
        cs.load(entry.instr_addr, byte_length)
        
        this_util=cs.count_invalid_entries() 
        if this_util>max_util:
            max_util=this_util
        if this_util<min_util:
            min_util=this_util
    if 'cache' in metrics:
        cs.print_stats()

    
    max_util=max_util*line_size
    min_util=min_util*line_size

    total_util=((max_util-min_util)/max_util)*100
    cache_dict['Level 1']['utilization(%)']=total_util
    
    # print(f"total_cache_utilization: {total_util:.2f}%")
    

    # total_lines= no_of_sets*no_of_ways
    # unutilized_lines=cs.count_invalid_entries()
    # cache_utilization=((total_lines-unutilized_lines)/total_lines)*100
    # print(f"cache_utilization: {cache_utilization:.2f}%")
    return(cache_list,cache_dict)

