import math


# reads the configuration of the table/caches from the config file provided
# prints and returns a dictionary with all configuration values
def read_config(file):
    config_dict = {}
    with open(file, 'r') as config:
        content = config.read()
        heirarchies = content.split("\n\n")

        # TODO: Validations are remaining
        for component in heirarchies:
            component_data = component.splitlines()

            if "Data TLB" in component_data[0]:
                tlb_sets = int(component_data[1].split(":")[-1])
                tlb_set_size = int(component_data[2].split(":")[-1])
                tlb_bits = int(math.log2(tlb_sets))
                print(f"Data TLB contains {tlb_sets} sets.")
                print(f"Each set contains {tlb_set_size} entries.")
                print(f"Number of bits used for the index is {tlb_bits}.")
                config_dict.update({'Data TLB':{
                    'Set' : tlb_sets,
                    'Set Size' : tlb_set_size,
                    'Set' : tlb_sets,
                    'Index Bits': tlb_bits
                    }
                })

            elif "Page Table" in component_data[0]:
                virtual_pages = int(component_data[1].split(":")[-1])
                physical_pages = int(component_data[2].split(":")[-1])
                page_size = int(component_data[3].split(":")[-1])
                page_index_bits = int(math.log2(virtual_pages))
                page_offset_bits = int(math.log2(page_size))
                print(f"\nNumber of virtual pages is {virtual_pages}.")
                print(f"Number of physical pages is {physical_pages}.")
                print(f"Each page contains {page_size} bytes.")
                print(f"Number of bits used for the page table index is {page_index_bits}.")
                print(f"Number of bits used for the page offset is {page_offset_bits}.")
                config_dict.update({'Page Table':{
                    'Virtual Pages' : virtual_pages,
                    'Physical Pages' : physical_pages,
                    'Page Size' : page_size,
                    'Index Bits' : page_index_bits,
                    'Offset Bits' : page_offset_bits,
                    }
                })

            elif "Data Cache" in component_data[0]:
                dc_sets = int(component_data[1].split(":")[-1])
                dc_set_size = int(component_data[2].split(":")[-1])
                dc_line_size = int(component_data[3].split(":")[-1])
                dc_write_policy = "no write-allocate and write-through" if component_data[4].split(":")[-1].strip() == "y" else "write-allocate and write-back"
                dc_index_bits = int(math.log2(dc_sets))
                dc_offset_bits = int(math.log2(dc_line_size))
                print(f"\nD-cache contains {dc_sets} sets.")
                print(f"Each set contains {dc_set_size} entries.")
                print(f"Each line is {dc_line_size} bytes.")
                print(f"The cache uses a {dc_write_policy} policy.")
                print(f"Number of bits used for the index is {dc_index_bits}.") # calculate this
                print(f"Number of bits used for the offset is {dc_offset_bits}.") # calculate this
                config_dict.update({'Data Cache' : {
                        'Sets': dc_sets,
                        'Set Size' : dc_set_size,
                        'Line Size': dc_line_size,
                        'Write Policy' : dc_write_policy,
                        'Index Bits' : dc_index_bits,
                        'Offset Bits' : dc_offset_bits,
                    }
                })

            elif "L2 Cache" in component_data[0]:
                l2_cache_sets = int(component_data[1].split(":")[-1])
                l2_cache_set_size = int(component_data[2].split(":")[-1])
                l2_cache_line_size = int(component_data[3].split(":")[-1])
                l2_cache_write_policy = "Write back/write allocate"
                l2_cache_index_bits = int(math.log2(l2_cache_sets))
                l2_cache_offset_bits = int(math.log2(l2_cache_line_size))
                print(f"\nL2-cache contains {l2_cache_sets} sets.")
                print(f"Each set contains {l2_cache_set_size} entries.")
                print(f"Each line is {l2_cache_line_size} bytes.")
                print(f"Number of bits used for the index is {l2_cache_index_bits}.") #calculate this
                print(f"Number of bits used for the offset is {l2_cache_offset_bits}.") # calculate this
                config_dict.update({'L2 Cache':{
                        'Sets': l2_cache_sets,
                        'Set Size' : l2_cache_set_size,
                        'Line Size': l2_cache_line_size,
                        'Write Policy' : l2_cache_write_policy,
                        'Index Bits' : l2_cache_index_bits,
                        'Offset Bits' : l2_cache_offset_bits,
                    }
                })

            else:
                component_data = component.split("\n")
                virtual_address = False
                tlb = False
                l2_cache = False
                for values in component_data:
                    temp = values.split(": ")[-1].strip()
                    if "Virtual addresses" in values:
                        if temp == 'y':
                            virtual_address = True
                        else:
                            virtual_address = False
                    if "TLB" in values:
                        tlb = True if temp == 'y' else False
                    if "L2 cache" in values:
                        l2_cache = True if temp == 'y' else False

                config_dict.update({
                    'Virtual Address': virtual_address,
                    'TLB Access' : tlb,
                    'L2 Access': l2_cache,
                })
        return config_dict

# read the trace data references from the provided file and returns binary output of enough length
def read_trace_data(file):
    trace_data = []
    with open(file, "r") as file:
        content = file.read().splitlines()
        for line in content:
            reference = line.split(":")
            integer = int(reference[1], 16)
            address = bin(integer)[2:]
            address = "0"*(4*16 - len(address)) +  address # pad 0s for 16 bit
            trace_data.append((reference[0], address))
    return trace_data

# function to print the final hex addresses, miss or hit
def format_value(value):
    # Convert integers to hexadecimal strings, keep strings as they are
    if isinstance(value, int):
        return f"{value:x}"
    if value and "0x" in value:
        return f"{int(value, 16):08x}"
    return value
