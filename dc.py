import state


# invalidate dc lines for the l2 lines that are being replaced
def invalidate_dc(address, dirty = 0):
    from l2 import simulate_read_l2

    start = state.config_data["Data Cache"]["Offset Bits"]
    end = start + state.config_data["Data Cache"]["Index Bits"]
    index = int(address[-end:-start], 2)
    tag = int(address[:-end], 2)

    if index in state.dc_table:
        row = state.dc_table[index]
        for i in range(1, len(row)):
            if "valid" in row[i] and row[i]["valid"] == 1 and row[i]["tag"] == tag:  # check which set to look for
                if row[i]["dirty_bit"] == 1:
                    if state.l2_access:
                        simulate_read_l2(address, 1)
                        state.l2_hit += 1
                    else:
                        state.main_memory_refs += 1
                row[i]["valid"] = 0
    return

# simulate dc to calculate hit/miss
def simulate_read_dc(address, dirty):
    from l2 import simulate_read_l2

    start = state.config_data["Data Cache"]["Offset Bits"]
    end = start + state.config_data["Data Cache"]["Index Bits"]
    index = int(address[-end:-start], 2)
    tag = int(address[:-end], 2)
    index_len = end - start
    tag_len = len(address) - end

    dc_set_size = state.config_data["Data Cache"]["Set Size"]
    status = "miss"
    if index in state.dc_table:
        row = state.dc_table[index]
        for i in range(1, len(row)):
            if "valid" in row[i] and row[i]["valid"] == 1 and row[i]["tag"] == tag:  # check which set to look for
                status = "hit"
                replace_set = i
                l2_status, l2_tag, l2_index = None, None, None
                break
        else:
            replace_set = row[0].pop(0) + 1 # Adjustment for LRU
            # write to l2 first and then to dc
            if state.l2_access:
                # if the new block replaces a line, write the old line back to l2
                if row[replace_set]["valid"] == 1 and row[replace_set]["dirty_bit"] == 1:
                    replaced_dirty = row[replace_set]["dirty_bit"]

                    replaced_tag = bin(row[replace_set]["tag"])[2:]
                    replaced_tag = "0"*(tag_len - len(replaced_tag)) + replaced_tag

                    replaced_index = bin(replace_set - 1)[2:]
                    replaced_index = "0"*(index_len - len(replaced_index)) + replaced_index

                    replaced_address = replaced_tag + replaced_index + address[-start:]
                    simulate_read_l2(replaced_address, replaced_dirty)
                    state.l2_hit += 1
                l2_status, l2_tag, l2_index = simulate_read_l2(address, 0)

            else:
                if row[replace_set]["dirty_bit"] == 1:
                    state.main_memory_refs += 1
                l2_status, l2_tag, l2_index = None, None, None

            row[replace_set].update({
                "valid" : 1,
                "tag" : tag, # check for page replacement
                "dirty_bit" : dirty
            })
        row[0].append(replace_set-1) # adjust for more than 2 sets
    else:
        # write to l2 first and then to dc
        if state.l2_access:
            l2_status, l2_tag, l2_index = simulate_read_l2(address, 0)
        else:
            l2_status, l2_tag, l2_index = None, None, None
        dc_indices = [i for i in range(1, dc_set_size)]
        state.dc_table.update({
            index:[
                dc_indices,
            {
                "valid": 1,
                "tag" : tag, # check for page replacement
                "dirty_bit": dirty
            }, # set 0
           ]
        })
        # empty sets initialization
        for _ in range(dc_set_size - 1):
            state.dc_table[index].append({
                "valid": 0,
                "tag" : None, # check for page replacement
                "dirty_bit": 0
            })
        state.dc_table[index][0].append(0) # adjust for more than 2 sets
    if status == "miss" and not state.l2_access:
        state.main_memory_refs += 1
    return status, tag, index, l2_status, l2_tag, l2_index

# write to dc
def simulate_write_dc(address):
    from l2 import simulate_read_l2

    start = state.config_data["Data Cache"]["Offset Bits"]
    end = start + state.config_data["Data Cache"]["Index Bits"]
    index = int(address[-end:-start], 2)
    tag = int(address[:-end], 2)

    status = "miss"
    l2_status, l2_tag, l2_index = None, None, None
    if index in state.dc_table:
        row = state.dc_table[index]
        replace_set = row[0].pop(0) + 1 if len(row[0]) > 0 else 1 # Adjustment for LRU
        for i in range(1, len(row)):
            if "valid" in row[i] and row[i]["valid"] == 1 and row[i]["tag"] == tag:  # check which set to look for
                status = "hit"
                replace_set = i
                break
        row[0].append(replace_set-1)

    if status == "miss":
        if state.l2_access:
            l2_status, l2_tag, l2_index = simulate_read_l2(address, 1)
        else:
            state.main_memory_refs += 1
    return status, tag, index, l2_status, l2_tag, l2_index
