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
    """
    An implementation of Uniform Cost Search.
    Very similar to our implementation A* search, but it makes some slight optimizations compared to running A* with a
    heuristic function that always returns 1.
    :param initial_state: The state to start the search on.
    :return: See `resultify`
    """
    closed_set = set()
    open_set = [initial_state]
    search_graph = nx.Graph()
    search_graph.add_node(hash(initial_state), status="open", start=True)

    while len(open_set) != 0:
        current = open_set.pop()
        closed_set.add(current)
        search_graph.node[hash(current)]['status'] = 'closed'
        if current.is_goal():
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
    """
    A simple non-optimal Greedy search. It runs very quickly and produces nearly optimal results on a random grid.
    There are certain grids, however that this algorithm does not work with.
    :param initial_state: The state to start the search on.
    :return: See `resultify`
    """
    current = initial_state
    while not current.is_goal():
        current = max(current.successors(), key=lambda x: len(x.graph.node[x.head_node]['blocks']))
    return resultify(current)


def a_star(initial_state):
    """
    An implementation of the A* Search Algorithm.
    :param initial_state: The state to start the search on.
    :return: See `resultify`.
    """
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
    """
    An incomplete Iterative Deepening A* Search. The current issue is that it does not return the optimal sequence of
    moves, just the number of moves that it needed to solve the puzzle. We did not put more effort into this because the
    increased memory efficiency was outweighed by the slow performance.
    :param initial_state: The starting state to do the search on.
    :return: The number of moves it took to get from the initial_state to a goal_state.
    """

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
    """
    Steps backwards through the final state of a search and accumulates usable results.
    :param final_state: The goal state that the search found.
    :param graph: An optional parameter for the search graph created in the search.
    :return: The number of moves required to complete the search, Each state in the order they happened, the search graph, a heat map representing the number of moves it took to consume each block in the initial grid representation.
    """
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
    """
    Writes a give graph as a json file to the given path.
    :param graph: The graph to write to the file.
    :param path: The location to write the file to.
    """
    json.dump(json_graph.node_link_data(graph), open(path, 'w'))


if __name__ == "__main__":
    print "test"
