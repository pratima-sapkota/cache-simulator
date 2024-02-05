# Shared global state for the memory hierarchy simulator

# initializes the tables/caches required to store data
tlb_table = dict()
page_table = dict()
l2_table = dict()
dc_table = dict()
config_data = dict()
l2_access = True

# variables to check count
l2_hit = 0
main_memory_refs = 0
disk_refs = 0
