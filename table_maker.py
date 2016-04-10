import os
import sys
import time
from ctypes import c_char_p, c_long, c_ulong, c_ulonglong
from multiprocessing import Value, Process

import numpy as py
import psutil

from Search import a_star, uniform_cost, iterative_deepening_a_star, greedy_search
from State import State, RedundantCheckingState

"""
This program runs all of our searches an measures their runtime, memory usage and the number of moves it solved the
puzzle in.

To do this, it runs each search within its own process to accurately measure RAM usage.

This will take up to several hours to run and will use upwards of 24 GB of RAM.

Each search function has exactly 10 minutes to run. If it fails to run within that timeframe, it will terminate and
output N/A for as its reported fields.

This was used to generate the data within our reports.
"""


def signal_handler(signum, frame):
    raise Exception("Timed out!")


def do_a_star(initial_state, timing, ram, moves):
    timet = time.time()
    num_moves, path, ngraph, heat_map = a_star(initial_state)
    timing.value = time.time() - timet
    moves.value = num_moves
    process = psutil.Process(os.getpid())
    ram.value = process.memory_info().peak_pagefile


def do_ucs(initial_state, timing, ram, moves):
    timet = time.time()
    num_moves, path, ngraph, heat_map = uniform_cost(initial_state)
    timing.value = time.time() - timet
    moves.value = num_moves
    process = psutil.Process(os.getpid())
    ram.value = process.memory_info().peak_pagefile


def do_ida_star(initial_state, timing, ram, moves):
    timet = time.time()
    num_moves = iterative_deepening_a_star(initial_state)
    timing.value = time.time() - timet
    moves.value = num_moves
    process = psutil.Process(os.getpid())
    ram.value = process.memory_info().peak_pagefile


def do_greedy(initial_state, timing, ram, moves):
    timet = time.time()
    num_moves = greedy_search(initial_state)[0]
    timing.value = time.time() - timet
    moves.value = num_moves
    process = psutil.Process(os.getpid())
    ram.value = process.memory_info().peak_pagefile


if __name__ == "__main__":
    # py.random.seed(0)
    timeout = 600
    print "size," \
          "colors," \
          "a*_moves_no_rc," \
          "a*_ram_no_rc," \
          "a*_time_no_rc," \
          "a*_moves_rc," \
          "a*_ram_rc," \
          "a*_time_rc," \
          "ucs_moves_no_rc," \
          "ucs_ram_no_rc," \
          "ucs_time_no_rc," \
          "ucs_moves_rc," \
          "ucs_ram_rc," \
          "ucs_time_rc," \
          "ida*_moves," \
          "ida*_ram," \
          "ida*_time," \
          "greedy_moves," \
          "greedy_ram," \
          "greedy_time"
    for n in range(2, 11):
        to = [False] * 6
        for c in range(2, 7):
            strings = [str(n) + "," + str(c)]
            t = py.random.randint(c, size=(n, n))
            no_rc = State(n, n, c, initial_values=t)
            rc = RedundantCheckingState(n, n, c, initial_values=t)

            timing = Value('d', 0.0)
            ram = Value(c_ulonglong, 0L)
            moves = Value('i', 0)
            ps = [Process(target=do_a_star, args=(no_rc, timing, ram, moves)),
                  Process(target=do_a_star, args=(rc, timing, ram, moves)),
                  Process(target=do_ucs, args=(no_rc, timing, ram, moves)),
                  Process(target=do_ucs, args=(rc, timing, ram, moves)),
                  Process(target=do_ida_star, args=(rc, timing, ram, moves)),
                  Process(target=do_greedy, args=(rc, timing, ram, moves))]
            for i, p in enumerate(ps):
                if to[i]:
                    strings.append("N/A,N/A,N/A")
                else:
                    p.start()
                    p.join(timeout=timeout)
                    if p.is_alive():
                        p.terminate()
                        to[i] = True
                        strings.append("N/A,N/A,N/A")
                    else:
                        strings.append(str(moves.value) + "," + str(ram.value) + "," + str(timing.value))
            print ",".join(strings)
