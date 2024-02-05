import state


# invalidating the entries in the dtlb whenever the page is replaced
def invalidate_dtlb(address, page_no):
    # invalidate here
    tlb_start = state.config_data["Page Table"]["Offset Bits"]
    tlb_end = tlb_start + state.config_data["Data TLB"]["Index Bits"]
    index = int(address[-tlb_end:-tlb_start], 2)
    tag = int(address[:-tlb_end], 2)

    if index in state.tlb_table:
        row = state.tlb_table[index]
        for i in range(1, len(row)):
            if "valid" in row[i] and row[i]["valid"] == 1 and row[i]["page"] == page_no:  # check which set to look for
                row[i]["valid"] = 0
    return

# simulate data tlb to calculate hit/miss
def simulate_tlb(address, mode):
    from page_table import simulate_page_table

    tlb_start = state.config_data["Page Table"]["Offset Bits"]
    tlb_end = tlb_start + state.config_data["Data TLB"]["Index Bits"]
    index = int(address[-tlb_end:-tlb_start], 2)
    tag = int(address[:-tlb_end], 2)

    status = "miss"
    page_status = "miss"
    tlb_set_size = state.config_data["Data TLB"]["Set Size"]

    virtual_page_no = int(address[:-tlb_start], 2) # everything except offset
    if index in state.tlb_table:
        row = state.tlb_table[index]
        for i in range(1, len(row)):
            if "valid" in row[i] and row[i]["valid"] == 1 and row[i]["tag"] == tag:  # check which set to look for
                status = "hit"
                page_no = row[i]["page"]
                replace_set = i
                break
        else:
            replace_set = row[0].pop(0) + 1 if len(row[0]) > 0 else 1 # Adjustment for LRU
            page_status, page_no, virtual_page_no = simulate_page_table(address, mode)
            row[replace_set].update({
                "valid" : 1,
                "tag" : tag,
                "page" : page_no
            })
        row[0].append(replace_set-1)
    else:
        page_status, page_no, virtual_page_no = simulate_page_table(address, mode)
        tlb_indices = [i for i in range(1, tlb_set_size)]
        state.tlb_table.update({
            index:[
                tlb_indices,
            {
                "valid": 1,
                "tag" : tag,
                "page": page_no
            }, # set 0
           ]
        })
        # empty row for remaining sets
        for _ in range(tlb_set_size - 1):
            state.tlb_table[index].append({
                "valid": 0,
                "tag" : None,
                "page": None
            })
        state.tlb_table[index][0].append(0)
    return status, tag, index, page_no, page_status, virtual_page_no
