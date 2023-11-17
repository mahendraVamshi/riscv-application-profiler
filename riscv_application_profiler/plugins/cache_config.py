from cachesim import CacheSimulator, Cache, MainMemory, CacheVisualizer
import riscv_application_profiler.consts as consts
from riscv_isac.log import *

'''Create one cache level out of given configuration.

:param sets: total number of sets, if 1 cache will be full-associative
:param ways: total number of ways, if 1 cache will be direct mapped
:param cl_size: number of bytes that can be addressed individually
:param replacement_policy: FIFO, LRU (default), MRU or RR
:param write_back: if true (default), write back will be done on evict.
                    Otherwise write-through is used
:param write_allocate: if true (default), a load will be issued on a
                        write miss
:param write_combining: if true, this cache will combine writes and
                        issue them on evicts(default is false)
:param subblock_size: the minimum blocksize that write-combining can
                        handle
:param load_from: the cache level to forward a load in case of a load
                    miss or write-allocate, if None, assumed to be main
                    memory
:param store_to: the cache level to forward a store to in case of
                    eviction of dirty lines, if None, assumed to be main
                    memory
:param victims_to: the cache level to forward any evicted lines to
                    (dirty or not)

The total cache size is the product of sets*ways*cl_size.
Internally all addresses are converted to cacheline indices.

Instantization has to happen from last level cache to first level
cache, since each subsequent level requires a reference of the other
level.
'''

main_mem = MainMemory()
def data_cache_configuration (level, lower_level, config):

    # mem,l2 = l2_cache_configuration('l2', config)
    mem = main_mem

    
    D_no_of_sets = config['profiles']['cfg']['data_cache']['no_of_sets']
    D_no_of_ways = config['profiles']['cfg']['data_cache']['no_of_ways']
    D_line_size = config['profiles']['cfg']['data_cache']['line_size']

    D_replacement_policy = config['profiles']['cfg']['data_cache']['replacement_policy']
    if config['profiles']['cfg']['data_cache']['write_back'] == True:
        D_write_back = True
    else:
        D_write_back = False

    if config['profiles']['cfg']['data_cache']['write_allocate'] == True:
        D_write_allocate = True
    else:
        D_write_allocate = False

    # total_cache_line = no_of_sets * no_of_ways
    # mem = MainMemory()
    D_cache_level = Cache(name = level, sets = D_no_of_sets, ways = D_no_of_ways, cl_size = D_line_size,
                 replacement_policy= D_replacement_policy,
                 write_back=D_write_back,
                 write_allocate=D_write_allocate,
                 write_combining=False,
                 subblock_size=None,
                 load_from=lower_level, store_to=lower_level, victims_to=None)
    # mem.load_to(cache_level)
    # mem.store_from(cache_level)
    D_cs = CacheSimulator(D_cache_level, mem)
    return mem,D_cs,D_cache_level


def instruction_cache_configuration(level, lower_level, config):

    mem = main_mem

    I_no_of_sets = config['profiles']['cfg']['instr_cache']['no_of_sets']
    I_no_of_ways = config['profiles']['cfg']['instr_cache']['no_of_ways']
    I_line_size = config['profiles']['cfg']['instr_cache']['line_size']
    I_replacement_policy = config['profiles']['cfg']['instr_cache']['replacement_policy']

    if config['profiles']['cfg']['instr_cache']['write_back'] == True:
        I_write_back = True
    else:
        I_write_back = False

    if config['profiles']['cfg']['instr_cache']['write_allocate'] == True:
        I_write_allocate = True
    else:
        I_write_allocate = False

    # total_cache_line = no_of_sets * no_of_ways

    # mem = MainMemory()
    # mem,l2 = l2_cache_configuration('l2', config)
    I_cache_level = Cache(name = level, sets = I_no_of_sets, ways = I_no_of_ways, cl_size = I_line_size,
                 replacement_policy= I_replacement_policy,
                 write_back=I_write_back,
                 write_allocate=I_write_allocate,
                 write_combining=False,
                 subblock_size=None,
                 load_from=lower_level, store_to=lower_level, victims_to=None)
    # mem.load_to(cache_level)
    # mem.store_from(cache_level)
    I_cs = CacheSimulator(I_cache_level, mem)

    return I_cs,I_cache_level


def l2_cache_configuration(level, lower_level, config):

    no_of_sets = config['profiles']['cfg']['l2_cache']['no_of_sets']
    no_of_ways = config['profiles']['cfg']['l2_cache']['no_of_ways']
    line_size = config['profiles']['cfg']['l2_cache']['line_size']
    replacement_policy = config['profiles']['cfg']['l2_cache']['replacement_policy']

    if config['profiles']['cfg']['l2_cache']['write_back'] == True:
        write_back = True
    else:
        write_back = False

    if config['profiles']['cfg']['l2_cache']['write_allocate'] == True:
        write_allocate = True
    else:
        write_allocate = False

    total_cache_line = no_of_sets * no_of_ways

    mem = main_mem
    cache_level = Cache(name = level, sets = no_of_sets, ways = no_of_ways, cl_size = line_size,
                 replacement_policy= replacement_policy,
                 write_back=write_back,
                 write_allocate=write_allocate,
                 write_combining=False,
                 subblock_size=None,
                 load_from=lower_level, store_to=lower_level, victims_to=None)
    mem.load_to(cache_level)
    mem.store_from(cache_level)
    # cs = CacheSimulator(cache_level, mem)

    return mem,cache_level