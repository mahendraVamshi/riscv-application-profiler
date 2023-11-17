
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
