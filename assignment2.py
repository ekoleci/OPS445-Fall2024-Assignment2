#!/usr/bin/env python3

'''
OPS445 Assignment 2
Program: assignment2.py 
Author: Enco Koleci
Semester: Fall 2024

The python code in this file is original work written by
Enco Koleci. No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or online resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: This script shows memory usage. It can show the whole
system memory usage or detailed memory usage.
'''

import argparse
import os

def parse_command_args() -> object:
    parser = argparse.ArgumentParser(description="Memory Visualiser -- See Memory Usage Report with bar charts", 
                                     epilog="Copyright 2024")
    parser.add_argument("-H", "--human-readable", action="store_true", help="Print sizes in human-readable format (e.g., MiB, GiB).")
    parser.add_argument("-l", "--length", type=int, default=20, help="Specify the length of the graph. Default is 20.")
    parser.add_argument("program", type=str, nargs='?', help="If a program is specified, show memory use of all associated processes. Show only total use if not.")
    return parser.parse_args()

def percent_to_graph(percent: float, length: int = 20) -> str:
    # Converts the  percentage value
    if percent < 0 or percent > 1:
        raise ValueError("Percent must be between 0 and 1.")
    filled_length = int(percent * length)
    return '#' * filled_length + ' ' * (length - filled_length)

def get_sys_mem() -> int:
    # gets all the system memory in Kib
    with open("/proc/meminfo", "r") as file:
        for line in file:
            if line.startswith("MemTotal:"):
                return int(line.split()[1])
    raise RuntimeError("Unable to retrieve system memory.")

def get_avail_mem() -> int:
    # Gets all the available system memory in Kib
    with open("/proc/meminfo", "r") as file:
        for line in file:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    raise RuntimeError("Unable to retrieve available memory.")

def pids_of_prog(app_name: str) -> list:
    # Returns a list of process IDs for a program name
    try:
        pids = os.popen(f"pidof {app_name}").read().strip().split()
        return pids
    except ValueError:
        return []

def rss_mem_of_pid(proc_id: int) -> int:
    """
    Calculates the Resident Set Size (RSS) memory used by a specific process
    """
    rss = 0
    try:
        with open(f"/proc/{proc_id}/smaps", "r") as file:
            for line in file:
                if line.startswith("Rss:"):
                    rss += int(line.split()[1])
    except FileNotFoundError:
        pass
    except PermissionError:
        pass
    return rss

def bytes_to_human_r(kibibytes: int, decimal_places: int = 2) -> str:
    # Converts the  memory from KiB to MiB, GiB, etc.
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suffix_index = 0
    size = kibibytes
    while size >= 1024 and suffix_index < len(suffixes) - 1:
        size /= 1024
        suffix_index += 1
    return f"{size:.{decimal_places}f} {suffixes[suffix_index]}"

if __name__ == "__main__":
    #processes the arguments and outputs memory usage
    args = parse_command_args()

    total_mem = get_sys_mem()
    avail_mem = get_avail_mem()
    used_mem = total_mem - avail_mem
    usage_percent = used_mem / total_mem

    if not args.program:
        #show total system memory usage
        bar = percent_to_graph(usage_percent, args.length)
        used_display = bytes_to_human_r(used_mem) if args.human_readable else f"{used_mem} KiB"
        total_display = bytes_to_human_r(total_mem) if args.human_readable else f"{total_mem} KiB"
        print(f"Memory         [{bar} | {int(usage_percent * 100)}%] {used_display}/{total_display}")
    else:
        #show  memory usage for a specific program
        pids = pids_of_prog(args.program)
        if not pids:
            print(f"{args.program} not found.")
        else:
            total_program_rss = 0
            for pid in pids:
                rss = rss_mem_of_pid(int(pid))
                total_program_rss += rss
                rss_percent = rss / total_mem
                rss_display = bytes_to_human_r(rss) if args.human_readable else f"{rss} KiB"
                bar = percent_to_graph(rss_percent, args.length)
                print(f"{pid:<15} [{bar} | {int(rss_percent * 100)}%] {rss_display}/{bytes_to_human_r(total_mem) if args.human_readable else f'{total_mem} KiB'}")

            total_percent = total_program_rss / total_mem
            total_rss_display = bytes_to_human_r(total_program_rss) if args.human_readable else f"{total_program_rss} KiB"
            bar = percent_to_graph(total_percent, args.length)
            print(f"{args.program:<15} [{bar} | {int(total_percent * 100)}%] {total_rss_display}/{bytes_to_human_r(total_mem) if args.human_readable else f'{total_mem} KiB'}")
