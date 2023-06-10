from cachesim import CacheSimulator, Cache, MainMemory
import riscv_application_profiler.consts as consts

def cache_simulator_example(master_inst_list, load_list, store_list):
    # #for i in range [0:10]:
    #print(master_inst_list[0])
    # print(load_list[1])
    # print(load_list[2])
    # print(load_list[3])
    # print(load_list[4])
    # print(store_list[0])
    print(len(load_list))
    print(len(store_list))

    mem = MainMemory()
    l1 = Cache("L1", 64, 4, 64, "RR")  # 64 sets, 4-ways with cacheline size of 64 bytes
    cs = CacheSimulator(l1, mem)

    #matching_dicts = [d for d in my_list if specific_key in d]

    for i in master_inst_list:
        if (i.reg_commit is None):
            continue
        else:
            consts.reg_file[f'x{i.reg_commit[1]}'] = i.reg_commit[2]
        if (i in load_list):
            # consts.reg_file[f'x{i.reg_commit[1]}'] = i.reg_commit[2]
            base = int(consts.reg_file[f'x{i.rs1[0]}'],16)
            if (i.imm is None):
                address = base
            else:
                address = base+i.imm
            if ('d' in i.instr_name):
                cs.load(address, length=8)
            if ('w' in i.instr_name):
                cs.load(address, length=4)
            if ('h' in i.instr_name):
                cs.load(address, length=2)
            if ('b' in i.instr_name):
                cs.load(address, length=1)
        if (i in store_list):
            base = int(consts.reg_file[f'x{i.rs1[0]}'],16)
            if (i.imm is None):
                address = base
            else:
                address = base+i.imm
            
            if ('d' in i.instr_name):
                cs.store(address, length=8)
            if ('w' in i.instr_name):
                cs.store(address, length=4)
            if ('h' in i.instr_name):
                cs.store(address, length=2)
            if ('b' in i.instr_name):
                cs.store(address, length=1)

    #cs.force_write_back()
    #cs.print_stats()