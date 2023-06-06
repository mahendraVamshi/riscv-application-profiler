from cachesim import CacheSimulator, Cache, MainMemory

def cache_simulator_example(load_list, store_list):
    print(load_list[0])
    print(store_list[0])

    mem = MainMemory()
    l1 = Cache("L1", 64, 4, 64, "RR")  # 64 sets, 4-ways with cacheline size of 64 bytes
    cs = CacheSimulator(l1, mem)

    for i in range(len(load_list)):
        address = load_list[i].rs1[0]+load_list[i].imm
        cs.load(address, length=8)

    cs.load(2342)  # Loads one byte from address 2342, should be a miss in all cache-levels
    cs.store(512, length=8)  # Stores 8 bytes to addresses 512-519,
                             # will also be a load miss (due to write-allocate)
    cs.load(512, length=8)  # Loads from address 512 until (exclusive) 520 (eight bytes)

    cs.force_write_back()
    cs.print_stats()