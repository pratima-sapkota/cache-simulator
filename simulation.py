import state
from config import format_value
from tlb import simulate_tlb
from page_table import simulate_page_table, physical_address
from dc import simulate_read_dc, simulate_write_dc


# simulate the memory hierarchy
def simulate_cache(data):
    tlb_access = state.config_data["TLB Access"]
    virtual_address = state.config_data["Virtual Address"]
    state.l2_access = state.config_data["L2 Access"]

    # count for hits, misses and memory references
    tlb_hit = 0
    tlb_miss = 0

    page_hit = 0
    page_miss = 0

    dc_hit = 0
    dc_miss = 0

    l2_miss = 0

    total_reads = 0
    total_writes = 0

    page_table_refs = 0

    # check if virtual address is on or not
    if virtual_address:
        addr_header = "Virtual"
        print("\nThe addresses read in are virtual addresses.")
        # check if tlb is on or not
        if not tlb_access:
            print("TLB is disabled in this configuration.")

    else:
        addr_header = "Physical"
        print("\nThe addresses read in are physical addresses.")
        # check if tlb is on or not
        if tlb_access:
            print("TLB can not be enabled when virtual address is disabled.")

    # check if l2 is enabled or not
    if not state.l2_access:
        print("L2 cache is disabled in this configuration.")

    print()
    print("{:8} {:6} {:4} {:6} {:3} {:4} {:4} {:4} {:6} {:3} {:4} {:6} {:3} {:}".format(addr_header, "Virt.","Page","TLB","TLB","TLB","PT","Phys","","DC","DC","","L2","L2"))
    print("{:8} {:6} {:4} {:6} {:3} {:4} {:4} {:4} {:6} {:3} {:4} {:6} {:3} {:4}".format("Address", "Page #","Off","Tag","Ind","Res.","Res.","Pg #","DC Tag","Ind","Res.","L2 Tag","Ind","Res."))
    print("{:8} {:6} {:4} {:6} {:3} {:4} {:4} {:4} {:6} {:3} {:4} {:6} {:3} {:4}".format("--------", "------","----","------","---","----","----","----","------","---","----","------","---","----"))

    for mode, address in data:
        vaddress = address

        if virtual_address:
            if tlb_access:
                tlb_status, tlb_tag, tlb_index, page_no, page_status, virtual_page_no = simulate_tlb(address, mode)
                if tlb_status == "hit":
                    tlb_hit += 1
                else:
                    tlb_miss +=1

            else:
                page_status, page_no, virtual_page_no = simulate_page_table(address, mode)
                tlb_status, tlb_tag, tlb_index = "", "", ""

            if not tlb_status == "hit" and page_status == "hit":
                page_hit += 1
            if not tlb_status == "hit" and page_status == "miss":
                page_miss += 1
                # disk_refs += 1

            # if tlb is on and is a hit, no need to go to page table
            if tlb_status == "hit":
                page_status = ""

            # calculate physical address
            address = physical_address(address, page_no)
        else:
            # if no virtual address, simulate page table for the physical page no
            address = address
            page_status, page_no, _ = simulate_page_table(address, mode)

            if page_status == "hit":
                page_hit += 1
            if page_status == "miss":
                page_miss +=1
                # disk_refs += 1

            tlb_status, tlb_tag, tlb_index, virtual_page_no = "", "", "", ""

        offset_bits = state.config_data["Page Table"]["Offset Bits"]
        page_offset = int(address[-offset_bits:], 2)

        #data cache simulation for read
        write_policy = state.config_data["Data Cache"]["Write Policy"]
        if mode == "R":
            dc_status, dc_tag, dc_index, l2_status, l2_tag, l2_index = simulate_read_dc(address, 0)
            total_reads += 1

        else:
            if write_policy == "write-allocate and write-back":
                dc_status, dc_tag, dc_index, l2_status, l2_tag, l2_index = simulate_read_dc(address, 1)
            else:
                dc_status, dc_tag, dc_index, l2_status, l2_tag, l2_index = simulate_write_dc(address)

            total_writes += 1

        if dc_status == "hit":
            dc_hit += 1
        else:
            dc_miss +=1
            if state.l2_access:
                if l2_status == "hit":
                    state.l2_hit += 1
                else:
                    l2_miss += 1
                    state.main_memory_refs += 1

        if dc_status == "hit" or not l2_status:
            l2_status, l2_tag, l2_index = "", "", ""

        variables = [hex(int(vaddress, 2)), virtual_page_no, page_offset, tlb_tag, tlb_index, tlb_status, page_status, page_no, dc_tag, dc_index, dc_status, l2_tag, l2_index, l2_status]
        # Pre-process the variables to convert integers to hexadecimal strings
        formatted_vars = [format_value(v) for v in variables]
        if not state.l2_access or dc_status == "hit":
            print("{:8} {:>6} {:>4} {:>6} {:>3} {:<4} {:<4} {:>4} {:>6} {:>3} {:<4} ".format(*formatted_vars))
        else:
            print("{:8} {:>6} {:>4} {:>6} {:>3} {:<4} {:<4} {:>4} {:>6} {:>3} {:<4} {:>6} {:>3} {:<4}".format(*formatted_vars))


    print("\nSimulation statistics")

    if virtual_address and tlb_access:
        page_table_refs = tlb_miss
    else:
        page_table_refs = page_hit + page_miss # verify once

    state.disk_refs = state.disk_refs + page_miss

    print()
    print(f"{'dtlb hits':<17}: {tlb_hit}")
    print(f"{'dtlb misses':<17}: {tlb_miss}")
    try:
        print(f"{'dtlb hit ratio':<17}: {tlb_hit/(tlb_hit + tlb_miss):.6f}")
    except:
        print(f"{'dtlb hit ratio':<17}: N/A")

    print()
    print(f"{'pt hits':<17}: {page_hit}")
    print(f"{'pt faults':<17}: {page_miss}")
    try:
        print(f"{'pt hit ratio':<17}: {page_hit/(page_hit + page_miss):.6f}")
    except:
        print(f"{'pt hit ratio':<17}: N/A")

    print()
    print(f"{'dc hits':<17}: {dc_hit}")
    print(f"{'dc misses':<17}: {dc_miss}")
    try:
        print(f"{'dc hit ratio':<17}: {dc_hit/(dc_hit + dc_miss):.6f}")
    except:
        print(f"{'dc hit ratio':<17}: N/A")

    print()
    print(f"{'L2 hits':<17}: {state.l2_hit}")
    print(f"{'L2 misses':<17}: {l2_miss}")
    try:
        print(f"{'L2 hit ratio':<17}: {state.l2_hit/(state.l2_hit + l2_miss):.6f}")
    except:
        print(f"{'L2 hit ratio':<17}: N/A")

    print()
    print(f"{'Total reads':<17}: {total_reads}")
    print(f"{'Total writes':<17}: {total_writes}")
    try:
        print(f"{'Ratio of reads':<17}: {total_reads/(total_reads + total_writes):.6f}")
    except:
        print(f"{'Ratio of reads':<17}: N/A")

    print()
    print(f"{'main memory refs':<17}: {state.main_memory_refs}")
    print(f"{'page table refs':<17}: {page_table_refs}")
    print(f"{'disk refs':<17}: {state.disk_refs}")

    return
