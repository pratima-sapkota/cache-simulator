# Assignment 2: Memory Hierarchy

# Completed by: PRATIMA SAPKOTA


# OBJECTIVE OF THE PROGRAM

# This program simulates the memory hierarchy given the configuration of the dtlb, page table and caches and the
# references of read/write data


# COMPILING THE PROGRAM

# This program can be run by:
# "python "<path/to/python/file>" "<path/to/trace>" "<path/to/config>"  > "<path/to/output>""
# If the command "python" does not work in linprog then program can be run by:
# "python3 "<path/to/python/file>" "<path/to/trace>" "<path/to/config>"  > "<path/to/output>""

# To run this program, Python 3.9+ is required which is available on linprog servers, already tested.
# If <path/to/trace> is not provided, the program terminates with an error message.
# If <path/to/config> is not provided, the program uses the one in the current directory.
# If "> <path/to/output>" is not provided the output is returned on the console.


import sys

import state
from config import read_config, read_trace_data
from simulation import simulate_cache


def main():
    # No. of arguments passed
    n = len(sys.argv)
    if n >= 2:
        if n > 2 and ".config" in sys.argv[2]:
            config_data_path = sys.argv[2]
        else:
            config_data_path = "trace.config"

        if ".dat" in sys.argv[1]:
            trace_data_path = sys.argv[1]
        else:
            print("Please provide the valid files: config file(.config) and trace data(.dat) file.")

        # Read configuration of caches
        state.config_data.update(read_config(config_data_path))
        # Read contents of trace data
        trace_data = read_trace_data(trace_data_path)

        if len(trace_data) > 0:
            # simulate the memory hierarchy
            simulate_cache(trace_data)
        else:
            print("\nThere are no data in the input file provided.")
    else:
        print("Please provide the required files: config file and trace data file.")


if __name__ == "__main__":
    main()
