import time
import json
import uuid
from State import State, ReduntantCheckingState

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
from networkx.readwrite import json_graph
from numpy import random, array
from sortedcontainers import SortedDict
from heapq import *


def uniform_cost(initial_state):
    start_time = time.time()
    closed_set = set()
    open_set = [initial_state]
    search_graph = nx.Graph()
    search_graph.add_node(hash(initial_state), status="open", start=True)

    while len(open_set) != 0:
        current = open_set.pop()
        closed_set.add(current)
        search_graph.node[hash(current)]['status'] = 'closed'
        if current.is_goal():
            print "\tNodes searched =", len(closed_set)
            print "\tNodes to be searched =", len(open_set)
            print "\tTime Taken =", (time.time() - start_time)
            return search_graph, reconstruct_path(current)
        for successor in current.successors():
            if successor not in closed_set:
                if successor not in open_set:
                    open_set.insert(0, successor)
                    search_graph.add_node(hash(successor), status="open")
                else:
                    i = open_set.index(successor)
                    if open_set[i].num_moves > successor.num_moves:
                        open_set[i] = successor
                search_graph.add_edge(hash(current), hash(successor), move=successor.last_move)

    raise LookupError("No path found")


def a_star(initial_state):
    start_time = time.time()
    closed_set = set()
    open_set = SortedDict()
    open_set[initial_state] = initial_state
    search_graph = nx.Graph()
    search_graph.add_node(hash(initial_state), status="open", start=True)
    while len(open_set) != 0:
        current = open_set.popitem(last=False)[1]
        closed_set.add(current)
        search_graph.node[hash(current)]['status'] = 'closed'
        if current.is_goal():
            print "\tNodes searched =", len(closed_set)
            print "\tNodes to be searched =", len(open_set)
            print "\tTime Taken =", (time.time() - start_time)
            return search_graph, reconstruct_path(current)

        for successor in current.successors():
            if successor not in closed_set:
                if successor not in open_set:
                    open_set[successor] = successor
                    search_graph.add_node(hash(successor), status="open")
                else:
                    open_successor = open_set[successor]
                    if successor.g_score() < open_successor.g_score():
                        open_set[successor] = successor
                search_graph.add_edge(hash(current), hash(successor), move=successor.last_move)
    raise LookupError("No path found")


def reconstruct_path(current):
    total_path = [current]
    while current.parent is not None:
        current = current.parent
        total_path.append(current)
    return list(reversed(total_path))


def write_graph_to_file(graph, path):
    json.dump(json_graph.node_link_data(graph), open(path, 'w'))


n = 10  # widths
m = 10  # height
c = 6  # number of colors
# initial state
t = random.randint(c, size=(m, n))
# t = array([[0, 0, 2, 2, 0, 1, 0, 0, 1, 0],
# [0, 2, 0, 2, 1, 1, 2, 2, 0, 1],
# [2, 0, 1, 2, 1, 0, 0, 0, 2, 1],
# [2, 1, 1, 0, 1, 1, 1, 2, 0, 1],
# [2, 2, 2, 0, 0, 1, 0, 1, 0, 0],
# [2, 1, 2, 0, 0, 2, 2, 2, 1, 2],
# [0, 2, 1, 2, 0, 2, 2, 1, 2, 2],
# [0, 2, 2, 0, 2, 2, 2, 0, 2, 0],
# [0, 1, 1, 0, 1, 1, 0, 1, 2, 0],
# [1, 2, 2, 0, 0, 0, 1, 0, 1, 2]])
print "Input is a {}x{} grid with {} colors.".format(n, m, c)
print t
print "\n"

# run search with A*
print "A* with redundancy:"
ngraph, path = a_star(State(n, m, c, None, initial_values=t))
print "Outcome:\n\t", len(path) - 1, "-", map(lambda x: x.last_move, path)[1:]
print "\n"
# output the search as a json graph.
ngraph.node[hash(path[-1])]['end'] = True
for i in range(len(path) - 1):
    ngraph.edge[hash(path[i])][hash(path[i + 1])]['optimal'] = True
write_graph_to_file(ngraph, 'static/a_star.json')

print "A* without redundancy:"
ngraph, path = a_star(ReduntantCheckingState(n, m, c, None, initial_values=t))
print "Outcome:\n\t", len(path) - 1, "-", map(lambda x: x.last_move, path)[1:]
print "\n"
ngraph.node[hash(path[-1])]['end'] = True
for i in range(len(path) - 1):
    ngraph.edge[hash(path[i])][hash(path[i + 1])]['optimal'] = True
write_graph_to_file(ngraph, 'static/uniform_cost.json')
print "Uniform Cost Search with redundancy:"
ngraph, path = uniform_cost(State(n, m, c, None, initial_values=t))
print "Outcome:\n\t", len(path) - 1, "-", map(lambda x: x.last_move, path)[1:]
print "\n"

print "Uniform Cost Search without redundancy:"
ngraph, path = uniform_cost(ReduntantCheckingState(n, m, c, None, initial_values=t))
print "Outcome:\n\t", len(path) - 1, "-", map(lambda x: x.last_move, path)[1:]
print "\n"



#
# # output the search as a json graph.
# ngraph2.node[hash(path2[-1])]['end'] = True
# for i in range(len(path2) - 1):
#     ngraph2.edge[hash(path2[i])][hash(path2[i + 1])]['optimal'] = True
# json.dump(json_graph.node_link_data(ngraph2), open('static/uniform_cost.json', 'w'))
