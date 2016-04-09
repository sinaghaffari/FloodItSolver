import time
import json

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
from networkx.readwrite import json_graph
import numpy as py
from sortedcontainers import SortedDict

from State import State, RedundantCheckingState


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
            # print "Uniform Cost:"
            # print "\tNodes searched =", len(closed_set)
            # print "\tNodes to be searched =", len(open_set)
            # print "\tTime Taken =", (time.time() - start_time)
            return resultify(current, search_graph)
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


def greedy_search(initial_state):
    start_time = time.time()
    current = initial_state
    while not current.is_goal():
        current = max(current.successors(), key=lambda x: len(x.graph.node[x.head_node]['blocks']))
    print "Greedy:"
    print "\tTime Taken =", (time.time() - start_time)
    return resultify(current)


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
            # print "A*:"
            # print "\tNodes searched =", len(closed_set)
            # print "\tNodes to be searched =", len(open_set)
            # print "\tTime Taken =", (time.time() - start_time)
            return resultify(current, search_graph)

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


def iterative_deepening_a_star(initial_state):
    def search(node, g, bound):
        f = g + node.h_score()
        if f > bound:
            return f
        if node.is_goal():
            return -1
        min_val = float('inf')
        for successor in node.successors():
            t = search(successor, g + 1, bound)
            if t == -1:
                return -1
            if t < min_val:
                min_val = t
        return min_val

    bound = initial_state.h_score()
    while True:
        t = search(initial_state, 0, bound)
        if t == -2:
            raise LookupError("No path found")
        if t == -1:
            return bound
        bound = t


def resultify(final_state, graph=nx.Graph()):
    total_path = [final_state]
    while final_state.parent is not None:
        final_state = final_state.parent
        total_path.append(final_state)
    grid = py.empty(shape=(final_state.height, final_state.width), dtype=int)
    num_moves = len(total_path) - 1
    for i in range(len(total_path)):
        s = total_path[i]
        for block in s.graph.node[s.head_node]['blocks']:
            x = block // s.width
            y = block % s.width
            grid[x][y] = num_moves * 2
        num_moves -= 1

    return len(total_path) - 1, list(reversed(total_path)), graph, grid


def write_graph_to_file(graph, path):
    json.dump(json_graph.node_link_data(graph), open(path, 'w'))


# n = 10  # widths
# m = 10  # height
# c = 3  # number of colors]
# py.random.seed(0)
# # initial state
# t = py.random.randint(c, size=(m, n))
# t = py.array([[0, 0, 2, 0, 2, 0, 3, 0, 1, 3],
#               [1, 1, 2, 2, 2, 1, 2, 2, 1, 2],
#               [3, 2, 2, 0, 2, 2, 0, 0, 0, 2],
#               [2, 0, 0, 3, 1, 1, 0, 1, 2, 0],
#               [2, 0, 3, 0, 3, 3, 1, 3, 0, 1],
#               [3, 2, 2, 3, 2, 0, 2, 0, 1, 1],
#               [3, 3, 0, 0, 2, 0, 3, 1, 1, 3],
#               [1, 3, 0, 1, 1, 1, 2, 3, 0, 0],
#               [0, 1, 3, 1, 1, 2, 1, 2, 2, 3],
#               [0, 0, 1, 0, 0, 1, 0, 2, 3, 3]])
# t = py.array([[0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#               [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#               [3, 2, 2, 2, 2, 2, 2, 2, 2, 2],
#               [3, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#               [3, 2, 2, 2, 2, 2, 2, 2, 2, 2],
#               [3, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#               [3, 2, 2, 2, 2, 2, 2, 2, 2, 2],
#               [3, 1, 1, 1, 1, 1, 1, 1, 1, 1],
#               [3, 2, 2, 2, 2, 2, 2, 2, 2, 2],
#               [3, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
# print "Input is a {}x{} grid with {} colors.".format(n, m, c)
# grid_string = "array(" + ",".join(",".join(string.strip().split(" ")) for string in str(t).split("\n")) + ")"
# print grid_string
# print "\n"
# state = RedundantCheckingState(n, m, c, None, initial_values=t)
# num_moves, path, ngraph, heat_map = a_star(state)
#
# print "A* took", len(path) - 1, "moves"
# print t, "\n"
# print heat_map
# plt.imshow(heat_map, interpolation='nearest')

# state.write_graph_to_file("static/force.json")
# # state.draw_graph()
#
#
#
# ngraph, path = a_star(state)
# ngraph.node[hash(path[-1])]['end'] = True
# for i in range(len(path) - 1):
#     ngraph.edge[hash(path[i])][hash(path[i + 1])]['optimal'] = True
# write_graph_to_file(ngraph, 'static/a_star.json')
#
# ngraph, path = uniform_cost(state)
# ngraph.node[hash(path[-1])]['end'] = True
# for i in range(len(path) - 1):
#     ngraph.edge[hash(path[i])][hash(path[i + 1])]['optimal'] = True
# write_graph_to_file(ngraph, 'static/uniform_cost.json')
#
# state = TestState(n, m, c, None, initial_values=t)
#
# ngraph, path = a_star(state)
# ngraph.node[hash(path[-1])]['end'] = True
# for i in range(len(path) - 1):
#     ngraph.edge[hash(path[i])][hash(path[i + 1])]['optimal'] = True
# write_graph_to_file(ngraph, 'static/a_star.json')
#
# ngraph, path = uniform_cost(state)
# ngraph.node[hash(path[-1])]['end'] = True
# for i in range(len(path) - 1):
#     ngraph.edge[hash(path[i])][hash(path[i + 1])]['optimal'] = True
# write_graph_to_file(ngraph, 'static/uniform_cost.json')
