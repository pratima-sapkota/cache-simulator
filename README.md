# Memory Hierarchy Simulator

A Python simulator for a multi-level memory hierarchy, including a Data TLB, Page Table, L1 Data Cache, and L2 Cache. The simulator processes memory trace files and reports hit/miss statistics for each level of the hierarchy.

## Architecture

The simulator models the following components in order of access:

```
Virtual Address
      |
  Data TLB ──(miss)──> Page Table
      |                     |
      └──(hit)──> Physical Address
                        |
                  L1 Data Cache
                        |
                    (miss)
                        |
                   L2 Cache
                        |
                    (miss)
                        |
                  Main Memory
```

- **Data TLB** (`tlb.py`) — Set-associative translation lookaside buffer with LRU replacement
- **Page Table** (`page_table.py`) — Virtual-to-physical page mapping with LRU replacement and dirty bit tracking
- **L1 Data Cache** (`dc.py`) — Set-associative data cache supporting write-back/write-allocate and write-through/no-write-allocate policies
- **L2 Cache** (`l2.py`) — Set-associative unified L2 cache with write-back/write-allocate policy

All components use **LRU (Least Recently Used)** replacement. On page replacement, the simulator correctly invalidates stale entries across the TLB, L1, and L2.

## Requirements

- Python 3.9+

No external dependencies are required.

## Usage

```sh
python memhier.py <trace_file.dat> [config_file.config]
```

| Argument | Required | Description |
|---|---|---|
| `trace_file.dat` | Yes | Memory access trace file |
| `config_file.config` | No | Cache/TLB configuration (defaults to `trace.config` in the current directory) |

To save output to a file:

```sh
python memhier.py trace.dat trace.config > output.txt
```

## Input File Formats

### Configuration File (`.config`)

Defines the parameters for each component, separated by blank lines:

```
Data TLB configuration
Number of sets: 4
Set size: 2

Page Table configuration
Number of virtual pages: 64
Number of physical pages: 8
Page size: 16

Data Cache configuration
Number of sets: 4
Set size: 1
Line size: 8
Write through/no write allocate: n

L2 Cache configuration
Number of sets: 16
Set size: 4
Line size: 8

Virtual addresses: y
TLB: y
L2 cache: y
```

The last section enables/disables virtual addressing, the TLB, and the L2 cache.

### Trace File (`.dat`)

Each line contains an access type and a hexadecimal address separated by a colon:

```
R:00a4f2
W:003ac1
R:00f391
```

- `R` = Read
- `W` = Write

## Output

The simulator prints:

1. **Configuration summary** — parsed parameters for each component
2. **Per-reference trace table** — virtual/physical address, page number, TLB/PT/DC/L2 tags, indices, and hit/miss results for each memory access
3. **Statistics summary** — hit counts, miss counts, and hit ratios for DTLB, Page Table, Data Cache, and L2 Cache, plus total reads/writes and memory/disk reference counts

## Project Structure

```
memhier.py       # Entry point — parses arguments, orchestrates simulation
config.py        # Reads configuration and trace files, formatting helpers
state.py         # Shared global state (tables, counters)
simulation.py    # Main simulation loop and statistics reporting
tlb.py           # Data TLB simulation
page_table.py    # Page table simulation and address translation
dc.py            # L1 Data Cache simulation (read/write paths)
l2.py            # L2 Cache simulation
```
