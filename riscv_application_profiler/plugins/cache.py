from cachesim import CacheSimulator, Cache, MainMemory
import riscv_application_profiler.consts as consts
from riscv_isac.log import *

def cache_simulator_example(master_inst_list, load_list, store_list):

    mem = MainMemory()
    l1 = Cache("L1", 64, 4, 64, "RR")  # 64 sets, 4-ways with cacheline size of 64 bytes
    mem.load_to(l1)
    mem.store_from(l1)
    cs = CacheSimulator(l1, mem)
    for i in range(10):
        logger.debug(print(load_list[i]))
    for i in master_inst_list:
        if (i.reg_commit is not None):
            consts.reg_file[f'x{i.reg_commit[1]}'] = i.reg_commit[2]
        if (i in load_list or i in store_list):
            base = int(consts.reg_file[f'x{i.rs1[0]}'],16)
            if ('d' in i.instr_name):
                byte_length = 8
            elif ('w' in i.instr_name):
                byte_length = 4
            elif ('h' in i.instr_name):
                byte_length = 2
            elif ('b' in i.instr_name):
                byte_length = 1
            if (i.imm is None):
                address = base
            else:
                address = base+i.imm
        if (i in load_list):
            cs.load(address, byte_length)
            
        elif (i in store_list):
            cs.store(address, byte_length)

    #cs.force_write_back()
    cs.print_stats()


