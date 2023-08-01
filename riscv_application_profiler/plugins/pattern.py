from riscv_isac.log import *
from riscv_application_profiler.consts import *
import re

def group_by_pattern(master_inst_list: list):
    '''
    Groups instructions based on the operation.

    Args:
        - master_inst_list: A list of InstructionEntry objects.

    Returns:
        - A 
    '''
    logger.info("Getting Pattern.")

    
    count_dict = {}
    pattern_dict = {}
    address_name_dict = {}
    address_cycle_dict = {}
    prev = None
    for entry in master_inst_list:
        if hex(entry.instr_addr) not in count_dict:
            count_dict[hex(entry.instr_addr)] = 0
            address_name_dict[hex(entry.instr_addr)] = entry.instr_name
            address_cycle_dict[hex(entry.instr_addr)] = 1
        count_dict[hex(entry.instr_addr)] += 1
    
    for entry in count_dict:
        if count_dict[entry] not in pattern_dict:
            pattern_dict[count_dict[entry]] = list()
        pattern_dict[count_dict[entry]].append(entry)

    sort_count_list= sorted(pattern_dict.items(), key=lambda x: x[0], reverse=True)
    for entry in sort_count_list:
        if len(entry[1]) == 1 or entry[0] == 1:
            sort_count_list.remove(entry)
    s_dict={'count':[],'instr':[],'cycles':[],'cycles_reduced':[]}
    for entry in sort_count_list:
        adj_inst = [address_name_dict[entry[1][0]]]
        adj_cycles = [address_cycle_dict[entry[1][0]]]
        prev = entry[1][0]
        for i in entry[1][1:]:
            if (int(i,16)-int(prev,16)) == 4 or (int(i,16)-int(prev,16)) == 2:
                adj_inst.append(address_name_dict[i])
                adj_cycles.append(address_cycle_dict[i])
            else:
                s_dict['instr'].append(adj_inst)
                s_dict['cycles'].append(adj_cycles)
                s_dict['count'].append(entry[0])
                adj_inst = [address_name_dict[i]]
                adj_cycles = [address_cycle_dict[i]]
            prev = i
        if len(adj_inst) > 1:
            s_dict['count'].append(entry[0])
            s_dict['cycles'].append(adj_cycles)
            s_dict['instr'].append(adj_inst)

    for i in range(len(s_dict['count'])):
        # total_cycles = s_dict['count'][i]*sum(s_dict['cycles'][i])
        # imp_performance = total_cycles - s_dict['count'][i]
        imp_performance = s_dict['count'][i]*(sum(s_dict['cycles'][i])-1)
        s_dict['cycles_reduced'].append(imp_performance)

    return(s_dict)
    # print(address_name_dict,sep='\n')
    # print(sort_count_list)


