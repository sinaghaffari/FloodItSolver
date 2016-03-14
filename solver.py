import time
import json
import uuid
from State import State

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
from networkx.readwrite import json_graph
from numpy import random, array
from sortedcontainers import SortedSet, SortedList
from heapq import heappop, heappush


def uniform_cost(start):
    start_time = time.time()
    closed_set = set()
    open_set = [start]
    camefrom = dict()

    graph = nx.Graph()
    graph.add_node(hash(start), status="open", start=True)
    while len(open_set) != 0:
        current = open_set.pop()
        closed_set.add(current)
        graph.node[hash(current)]['status'] = 'closed'
        if current.graph.number_of_nodes() == 1:
            # print "Nodes searched =", len(closed_set)
            # print "Nodes to be searched =", len(open_set)
            # print "Time Taken =", (time.time() - start_time)
            return graph, reconstruct_path(camefrom, current)

        for successor in current.successors():
            if successor in closed_set:
                graph.add_edge(hash(current), hash(successor), move=successor.last_move)
                continue
            tentative_cost = current.num_moves + 1
            if successor not in open_set:
                open_set.insert(0, successor)
            elif tentative_cost >= successor.num_moves:
                continue
            if not graph.has_node(hash(successor)):
                graph.add_node(hash(successor), status="open")
            graph.add_edge(hash(current), hash(successor), move=successor.last_move)
            camefrom[successor] = current
    raise LookupError("No path found")


def a_star(start):
    start_time = time.time()
    closed_set = set()
    open_set = []
    heappush(open_set, start)
    camefrom = dict()

    graph = nx.Graph()
    graph.add_node(hash(start), status="open", start=True)
    while len(open_set) != 0:
        current = heappop(open_set)
        closed_set.add(current)
        graph.node[hash(current)]['status'] = 'closed'
        if current.graph.number_of_nodes() == 1:
            print "Search Complete:"
            print "\tNodess searched =", len(closed_set)
            print "\tNodes to be searched =", len(open_set)
            print "\tTime Taken =", (time.time() - start_time)
            return graph, reconstruct_path(camefrom, current)

        for successor in current.successors():
            if successor in closed_set:
                graph.add_edge(hash(current), hash(successor))
                continue
            tentative_gscore = current.num_moves + 1
            if successor not in open_set:
                heappush(open_set, successor)
            elif tentative_gscore >= successor.num_moves:
                continue
            if not graph.has_node(hash(successor)):
                graph.add_node(hash(successor), status="open")
            graph.add_edge(hash(current), hash(successor), move=successor.last_move)

            camefrom[successor] = current
    raise LookupError("No path found")


def reconstruct_path(cameFrom, current):
    totalPath = [current]
    while current in cameFrom.keys():
        current = cameFrom[current]
        totalPath.append(current)
    return list(reversed(totalPath))


# Causes greedy to fail.
a = array([[0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
           [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
           [2, 1, 1, 1, 1, 1, 1, 1, 1, 1]])

# n = 10, m = 10, c = 4
a = array([[1, 1, 0, 0, 1, 0, 2, 1, 2, 0],
           [0, 1, 2, 0, 1, 2, 0, 3, 0, 3],
           [0, 1, 1, 0, 2, 0, 1, 0, 1, 2],
           [1, 3, 0, 0, 1, 0, 2, 1, 2, 2],
           [3, 1, 2, 1, 3, 1, 1, 3, 0, 2],
           [3, 3, 0, 3, 3, 3, 2, 3, 3, 0],
           [2, 1, 0, 3, 1, 2, 2, 1, 1, 1],
           [1, 1, 3, 3, 1, 1, 1, 0, 2, 1],
           [0, 2, 1, 0, 3, 3, 0, 0, 2, 3],
           [2, 0, 1, 2, 3, 1, 0, 3, 0, 2]])

# n = 10, m = 10, c = 3
a = array([[1, 1, 0, 0, 2, 0, 0, 1, 0, 2],
           [0, 2, 2, 0, 0, 1, 1, 0, 0, 1],
           [2, 1, 2, 1, 0, 2, 2, 2, 0, 1],
           [2, 1, 0, 1, 0, 0, 0, 1, 0, 2],
           [0, 2, 1, 1, 0, 2, 2, 2, 2, 0],
           [1, 2, 0, 0, 0, 0, 1, 1, 1, 1],
           [1, 1, 0, 1, 2, 1, 0, 0, 2, 2],
           [0, 1, 1, 1, 0, 2, 0, 0, 0, 1],
           [2, 2, 1, 0, 2, 2, 1, 0, 0, 0],
           [1, 0, 0, 1, 2, 0, 0, 1, 1, 0]])

# the gracefu test.
a = array([[1, 1, 2, 2, 1],
           [0, 1, 1, 1, 2],
           [1, 0, 0, 1, 1],
           [1, 0, 1, 2, 2],
           [1, 0, 2, 0, 1]])

# 20x20 with 6 colors
a = array([[0, 1, 2, 0, 2, 5, 4, 2, 2, 0, 0, 3, 5, 2, 1, 3, 2, 5, 3, 1],
           [0, 0, 0, 0, 4, 1, 5, 3, 5, 1, 4, 3, 2, 3, 2, 0, 5, 2, 2, 3],
           [0, 3, 1, 4, 1, 1, 5, 0, 1, 4, 0, 2, 5, 5, 1, 0, 3, 5, 1, 5],
           [5, 0, 2, 4, 5, 4, 3, 3, 4, 2, 1, 3, 5, 0, 4, 5, 5, 5, 3, 1],
           [0, 3, 3, 2, 4, 0, 5, 0, 0, 0, 4, 3, 4, 0, 2, 3, 2, 1, 2, 3],
           [5, 2, 2, 4, 5, 0, 3, 5, 4, 2, 3, 3, 2, 5, 1, 0, 1, 1, 1, 3],
           [0, 5, 3, 1, 1, 3, 4, 0, 4, 0, 2, 3, 0, 3, 2, 5, 1, 2, 1, 2],
           [0, 3, 3, 2, 1, 4, 1, 5, 3, 1, 3, 5, 0, 5, 5, 1, 1, 3, 2, 5],
           [1, 5, 1, 5, 1, 4, 3, 0, 3, 3, 0, 1, 3, 1, 3, 5, 1, 2, 5, 0],
           [3, 3, 0, 2, 5, 0, 5, 3, 4, 1, 0, 0, 5, 2, 5, 3, 4, 5, 1, 0],
           [1, 4, 2, 4, 3, 5, 1, 2, 0, 5, 2, 0, 2, 4, 1, 0, 0, 2, 2, 3],
           [0, 2, 5, 2, 0, 3, 5, 4, 1, 0, 4, 2, 0, 0, 2, 2, 4, 1, 3, 1],
           [3, 0, 1, 1, 3, 0, 0, 0, 2, 5, 5, 3, 5, 1, 1, 1, 1, 0, 4, 1],
           [2, 4, 1, 1, 2, 4, 5, 5, 1, 1, 2, 1, 5, 3, 4, 0, 5, 2, 2, 1],
           [3, 2, 3, 5, 1, 5, 3, 1, 0, 5, 3, 0, 5, 0, 4, 3, 5, 5, 3, 0],
           [3, 5, 4, 1, 4, 0, 2, 1, 0, 5, 3, 4, 0, 0, 0, 4, 4, 3, 4, 4],
           [1, 2, 4, 5, 5, 2, 2, 2, 5, 5, 1, 4, 3, 4, 2, 0, 4, 3, 4, 0],
           [2, 2, 1, 0, 5, 1, 5, 4, 5, 3, 3, 4, 5, 3, 2, 5, 5, 3, 4, 0],
           [0, 5, 0, 4, 4, 3, 0, 5, 5, 1, 2, 5, 1, 4, 0, 2, 1, 5, 3, 1],
           [4, 2, 0, 3, 1, 2, 5, 5, 0, 2, 4, 1, 4, 5, 3, 2, 0, 2, 4, 2]])

a = array([[2, 1, 0, 2, 0, 0, 2, 0, 1, 2],
           [1, 1, 0, 2, 0, 1, 2, 0, 1, 2],
           [0, 2, 2, 0, 1, 1, 1, 2, 2, 1],
           [1, 0, 1, 1, 2, 0, 1, 2, 1, 0],
           [2, 2, 1, 2, 2, 2, 2, 2, 1, 1],
           [1, 0, 2, 0, 2, 0, 1, 0, 2, 2],
           [0, 2, 0, 1, 0, 0, 0, 0, 1, 2],
           [1, 0, 1, 2, 0, 0, 1, 0, 0, 0],
           [2, 2, 2, 0, 2, 0, 0, 0, 2, 0],
           [0, 2, 0, 2, 2, 2, 1, 0, 0, 2]])

n = 10  # width
m = 10  # height
c = 3  # number of colors

# initial state
s = State(n, m, c, None)

# output the state as a json graph.
d = json_graph.node_link_data(s.graph)
json.dump(d, open('static/force.json', 'w'))
# run search with A*
ngraph, path_moves = a_star(s)
print len(path_moves) - 1, "-", map(lambda x: x.last_move, path_moves)[1:]

# output the search as a json graph.
ngraph.node[hash(path_moves[-1])]['end'] = True
for i in range(len(path_moves) - 1):
    ngraph.edge[hash(path_moves[i])][hash(path_moves[i + 1])]['optimal'] = True
json.dump(json_graph.node_link_data(ngraph), open('static/a_star.json', 'w'))

# run search with uniform cost
# ngraph, path_moves = uniform_cost(s)
#
# # output the search as a json graph.
# ngraph.node[hash(path_moves[-1])]['end'] = True
# for i in range(len(path_moves) - 1):
#     ngraph.edge[hash(path_moves[i])][hash(path_moves[i + 1])]['optimal'] = True
# json.dump(json_graph.node_link_data(ngraph), open('static/uniform_cost.json', 'w'))
