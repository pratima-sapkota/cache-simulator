import state


# invalidate dc lines for l2 lines for the lines that are being replaced
def invalidate_l2(address, dirty = 0):
    from dc import invalidate_dc

    start = state.config_data["L2 Cache"]["Offset Bits"]
    end = start + state.config_data["L2 Cache"]["Index Bits"]
    index = int(address[-end:-start], 2)
    tag = int(address[:-end], 2)

    if index in state.l2_table:
        row = state.l2_table[index]
        for i in range(1, len(row)):
            if "valid" in row[i] and row[i]["valid"] == 1 and row[i]["tag"] == tag:  # check which set to look for
                invalidate_dc(address, dirty)
                if row[i]["dirty_bit"] == 1 or dirty == 1:
                    state.main_memory_refs += 1
                row[i]["valid"] = 0
    return

# simulate l2 for hit or miss
def simulate_read_l2(address, dirty):
    from dc import invalidate_dc

    start = state.config_data["L2 Cache"]["Offset Bits"]
    end = start + state.config_data["L2 Cache"]["Index Bits"]
    index_len = end - start
    tag_len = len(address) - end
    index = int(address[-end:-start], 2)
    tag = int(address[:-end], 2)

    l2_set_size = state.config_data["L2 Cache"]["Set Size"]
    status = "miss"
    if index in state.l2_table:
        row = state.l2_table[index]
        for i in range(1, len(row)):
            if "valid" in row[i] and row[i]["valid"] == 1 and row[i]["tag"] == tag:  # check which set to look for
                status = "hit"
                replace_set = i
                break
        else:
            replace_set = row[0].pop(0) + 1 # Adjustment for LRU
            # invalidate the line being replaced
            if row[replace_set]["valid"] == 1:
                replaced_tag = bin(row[replace_set]["tag"])[2:]
                replaced_tag = "0"*(tag_len - len(replaced_tag)) + replaced_tag

                replaced_index = bin(replace_set - 1)[2:]
                replaced_index = "0"*(index_len - len(replaced_index)) + replaced_index

                replaced_address = replaced_tag + replaced_index + address[-start:]
                invalidate_dc(replaced_address)
                if row[replace_set]["dirty_bit"] == 1:
                    state.main_memory_refs += 1

            row[replace_set].update({
                "valid" : 1,
                "tag" : tag, # check for page replacement
                "dirty_bit" : dirty
            })
        row[0].append(replace_set-1) # adjust for more than 2 sets

    else:
        lru_indices = [i for i in range(1, l2_set_size)]
        state.l2_table.update({
            index:[
                lru_indices,
            {
                "valid": 1,
                "tag" : tag, # check for page replacement
                "dirty_bit": dirty
            }, # set 0
           ]
        })
        for _ in range(l2_set_size - 1):
            state.l2_table[index].append({
                "valid": 0,
                "tag" : None, # check for page replacement
                "dirty_bit": 0
                })
        state.l2_table[index][0].append(0)
    return status, tag, index
