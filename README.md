# Cache Simulator

Use "make all sim_cache <BLOCKSIZE> <L1_SIZE> <L1_ASSOC> <L2_SIZE> <L2_ASSOC> <REPLACEMENT_POLICY> <INCLUSION_PROPERTY> <trace_file>" command in your terminal to run the project. 

o BLOCKSIZE: Positive integer. Block size in bytes. (Same block size for all caches in the memory hierarchy.)
o L1_SIZE: Positive integer. L1 cache size in bytes.
o L1_ASSOC: Positive integer. L1 set-associativity (1 is direct-mapped).
o L2_SIZE: Positive integer. L2 cache size in bytes. L2_SIZE = 0 signifies that there is no L2 cache.
o L2_ASSOC: Positive integer. L2 set-associativity (1 is direct-mapped). o REPLACEMENT_POLICY: Positive integer. 0 for LRU, 1 for FIFO, 2 for
optimal.
o INCLUSION_PROPERTY: Positive integer. 0 for non-inclusive, 1 for inclusive. o trace_file: Character string. Full name of trace file including any extensions.


implemented a flexible cache and memory hierarchy simulator and used it to compare the performance, area, and energy of different memory hierarchy configurations.

Designed a generic cache module that can be used at any level in a memory hierarchy. For example, this cache module can be “instantiated” as an L1 cache, an L2 cache, an L3 cache, and so on. Since it can be used at any level of the memory hierarchy, it will be referred to generically as CACHE throughout this specification.
