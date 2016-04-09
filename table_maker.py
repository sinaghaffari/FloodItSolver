import os
import sys
import time
from ctypes import c_char_p, c_long, c_ulong, c_ulonglong
from multiprocessing import Value, Process

import numpy as py
import psutil

from Search import a_star, uniform_cost, iterative_deepening_a_star
from State import State, RedundantCheckingState


def signal_handler(signum, frame):
    raise Exception("Timed out!")


def do_a_star(initial_state, timing, ram, moves):
    timet = time.time()
    num_moves, path, ngraph, heat_map = a_star(initial_state)
    timing.value = time.time() - timet
    moves.value = num_moves
    process = psutil.Process(os.getpid())
    ram.value = long(process.memory_info().peak_wset)


def do_ucs(initial_state, timing, ram, moves):
    timet = time.time()
    num_moves, path, ngraph, heat_map = uniform_cost(initial_state)
    timing.value = time.time() - timet
    moves.value = num_moves
    process = psutil.Process(os.getpid())
    ram.value = process.memory_info().peak_wset


def do_ida_star(initial_state, timing, ram, moves):
    timet = time.time()
    num_moves = iterative_deepening_a_star(initial_state)
    timing.value = time.time() - timet
    moves.value = num_moves
    process = psutil.Process(os.getpid())
    ram.value = process.memory_info().peak_wset


def do_greedy(initial_state, timing, ram, moves):
    timet = time.time()
    num_moves = iterative_deepening_a_star(initial_state)
    timing.value = time.time() - timet
    moves.value = num_moves
    process = psutil.Process(os.getpid())
    ram.value = process.memory_info().peak_wset


if __name__ == "__main__":
    py.random.seed(0)
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
        for c in range(2, 7):
            sys.stdout.write(str(n) + "," + str(c) + ",")
            t = py.random.randint(c, size=(n, n))
            no_rc = State(n, n, c, initial_values=t)
            rc = RedundantCheckingState(n, n, c, initial_values=t)

            timing = Value('d', 0.0)
            ram = Value(c_ulonglong, 0L)
            moves = Value('i', 0)

            p = Process(target=do_a_star, args=(no_rc, timing, ram, moves))
            p.start()
            p.join(timeout=600)
            if p.is_alive():
                p.terminate()
                sys.stdout.write("N/A,N/A,N/A,")
            else:
                sys.stdout.write(str(moves.value) + "," + str(ram.value) + "," + str(timing.value) + ",")

            p = Process(target=do_a_star, args=(rc, timing, ram, moves))
            p.start()
            p.join(timeout=600)
            if p.is_alive():
                p.terminate()
                sys.stdout.write("N/A,N/A,N/A,")
            else:
                sys.stdout.write(str(moves.value) + "," + str(ram.value) + "," + str(timing.value) + ",")

            p = Process(target=do_ucs, args=(no_rc, timing, ram, moves))
            p.start()
            p.join(timeout=600)
            if p.is_alive():
                p.terminate()
                sys.stdout.write("N/A,N/A,N/A,")
            else:
                sys.stdout.write(str(moves.value) + "," + str(ram.value) + "," + str(timing.value) + ",")

            p = Process(target=do_ucs, args=(rc, timing, ram, moves))
            p.start()
            p.join(timeout=600)
            if p.is_alive():
                p.terminate()
                sys.stdout.write("N/A,N/A,N/A,")
            else:
                sys.stdout.write(str(moves.value) + "," + str(ram.value) + "," + str(timing.value) + ",")

            p = Process(target=do_ida_star, args=(rc, timing, ram, moves))
            p.start()
            p.join(timeout=600)
            if p.is_alive():
                p.terminate()
                sys.stdout.write("N/A,N/A,N/A,")
            else:
                sys.stdout.write(str(moves.value) + "," + str(ram.value) + "," + str(timing.value) + ",")

            p = Process(target=do_greedy, args=(rc, timing, ram, moves))
            p.start()
            p.join(timeout=600)
            if p.is_alive():
                p.terminate()
                sys.stdout.write("N/A,N/A,N/A")
            else:
                sys.stdout.write(str(moves.value) + "," + str(ram.value) + "," + str(timing.value))
            print ""
