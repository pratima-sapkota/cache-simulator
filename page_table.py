import state


# convert virtual address to physical address given the page number
def physical_address(address, index):
    page_start = state.config_data["Page Table"]["Offset Bits"] # offset for physical and virtual page is same
    page_index_bits = state.config_data["Page Table"]["Index Bits"]
    page_end = page_start + page_index_bits
    index = bin(index)[2:]
    index = "0"* (page_index_bits - len(index)) + index
    phys_address = address[:-page_end] + index + address[-page_start:]
    return phys_address

# invalidating the entries in the page table whenever the page is replaced
def invalidate_page_table(page_no):
    from tlb import invalidate_dtlb
    from l2 import invalidate_l2
    from dc import invalidate_dc

    for _, row in state.page_table.items():
        if "page" in row and row["page"] == page_no and row["valid"] == 1:
            replaced_address = row["address"]
            if state.config_data["TLB Access"]:
                invalidate_dtlb(replaced_address, page_no)

            dirty = row["dirty_bit"]
            if state.config_data["L2 Access"]:
                invalidate_l2(physical_address(replaced_address, page_no), dirty)
            else:
                invalidate_dc(physical_address(replaced_address, page_no), dirty)
            row["valid"] = 0

            if dirty == 1:
                state.disk_refs += 1
    return

# simulating the entries in the page table to calculate if its a hit/miss
def simulate_page_table(address, mode):
    start = state.config_data["Page Table"]["Offset Bits"] # offset for physical and virtual page is same
    index_bits = state.config_data["Page Table"]["Index Bits"]
    end = start + index_bits
    index = int(address[-end:-start], 2)
    page_size = state.config_data["Page Table"]["Physical Pages"]

    virtual_page_no = int(address[:-start], 2) # everything except offset
    dirty_bit = 0 if mode == "R" else 1
    status = "miss"
    if not "lru" in state.page_table:
        state.page_table["lru"] = [i for i in range(page_size)]

    if index in state.page_table:
        row = state.page_table[index]
        if row["valid"] == 1:
            page_no = row["page"]
            row.update({"dirty_bit": dirty_bit})
            status = "hit"
            state.page_table["lru"].remove(page_no) # send to the last used one
        else:
            # take the first element for least recently used
            page_no = state.page_table["lru"].pop(0)
            # check for replaced page, invalidate DC, L2 and DTLB
            invalidate_page_table(page_no)

            row.update({
                "dirty_bit": dirty_bit,
                "page": page_no,
                "valid": 1,
                "address": address
            })
    else:
        # take the first element for least recently used
        page_no = state.page_table["lru"].pop(0)
        # check for replaced page, invalidate DC, L2 and DTLB
        invalidate_page_table(page_no)
        # create a new row for the new index
        state.page_table.update({
            index:
            {
                "dirty_bit": dirty_bit,
                "page": page_no,
                "valid": 1,
                "address": address
            }, # set 0
        })
    # append to last as it's most recently used now
    state.page_table["lru"].append(page_no)
    return status, page_no, virtual_page_no
