import json
import uuid

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
from networkx.readwrite import json_graph
import numpy as py
import random as rand
from copy import deepcopy

__author__ = 'sina'

colord = {
    0: '#ff0000',
    1: '#00ff00',
    2: '#0000ff',
    3: '#ffff00',
    4: '#ff00ff',
    5: '#00ffff'
}


class _State:
    def __init__(self, width, height, num_colors, last_move=None, parent=None, num_moves=0, head_node=None,
                 initial_values=None, initial_graph=None):
        self.parent = parent
        self.last_move = last_move
        self.num_moves = num_moves
        self.width = width
        self.height = height
        self.num_colors = num_colors
        if initial_values is None and initial_graph is None:
            self.graph, self.head_node = self.create_graph(py.random.randint(num_colors, size=(height, width)))
        elif initial_values is None and initial_graph is not None:
            self.graph = initial_graph
            self.head_node = head_node
        elif initial_values is not None and initial_graph is None:
            self.graph, self.head_node = self.create_graph(initial_values)
        self.id = hash(self.graph.node[self.head_node]['blocks'])
        self.estimated_moves_to_goal = None

    def create_grid(self, graph):
        values = py.array([[0] * self.width] * self.height)
        graph_map = py.array([[''] * self.width] * self.height, dtype=object)
        for node in graph.nodes(data=True):
            for block in node[1]['blocks']:
                x = block // self.width
                y = block % self.width
                values[x][y] = node[1]['color']
                graph_map[x][y] = node[0]
        return values

    def create_graph(self, values):
        color_map = py.array([[''] * self.width] * self.height, dtype=object)
        graph = nx.Graph()

        def flood_fill(x, y, value):
            initial_value = values[y][x]
            attr_dict = {'blocks': frozenset(), 'color': initial_value}
            if x == 0 and y == 0:
                attr_dict['root'] = True
            graph.add_node(value, attr_dict=attr_dict)
            visited = []
            queue = [(y, x)]
            while len(queue) != 0:
                current = queue.pop()
                visited.append(current)
                color_map[current[0]][current[1]] = value
                graph.node[value]['blocks'] = graph.node[value]['blocks'].union(
                    frozenset([current[0] * self.width + current[1]]))
                if current[0] + 1 < self.height and (current[0] + 1, current[1]) not in queue:
                    if values[current[0] + 1][current[1]] == initial_value:
                        if (current[0] + 1, current[1]) not in visited:
                            queue.insert(0, (current[0] + 1, current[1]))
                    else:
                        if color_map[current[0] + 1][current[1]] != '':
                            graph.add_edge(value, color_map[current[0] + 1][current[1]])
                if current[0] - 1 >= 0 and (current[0] - 1, current[1]) not in queue:
                    if values[current[0] - 1][current[1]] == initial_value:
                        if (current[0] - 1, current[1]) not in visited:
                            queue.insert(0, (current[0] - 1, current[1]))
                    else:
                        if color_map[current[0] - 1][current[1]] != '':
                            graph.add_edge(value, color_map[current[0] - 1][current[1]])
                if current[1] + 1 < self.width and (current[0], current[1] + 1) not in queue:
                    if values[current[0]][current[1] + 1] == initial_value:
                        if (current[0], current[1] + 1) not in visited:
                            queue.insert(0, (current[0], current[1] + 1))
                    else:
                        if color_map[current[0]][current[1] + 1] != '':
                            graph.add_edge(value, color_map[current[0]][current[1] + 1])
                if current[1] - 1 >= 0 and (current[0], current[1] - 1) not in queue:
                    if values[current[0]][current[1] - 1] == initial_value:
                        if (current[0], current[1] - 1) not in visited:
                            queue.insert(0, (current[0], current[1] - 1))
                    else:
                        if color_map[current[0]][current[1] - 1] != '':
                            graph.add_edge(value, color_map[current[0]][current[1] - 1])

        count = 0
        for i in range(len(values)):
            for j in range(len(values[i])):
                if color_map[i][j] == '':
                    flood_fill(j, i, count)
                    count += 1
        return graph, color_map[0][0]

    def successors(self):
        return [self.do_move(x) for x in self.valid_actions()]

    def do_move(self, move):
        new_graph = nx.Graph()
        new_graph.add_nodes_from(self.graph.nodes(data=True))
        new_graph.add_edges_from(self.graph.edges())

        affected_children = filter(lambda x: new_graph.node[x]['color'] == move, new_graph.neighbors(self.head_node))
        gained_blocks = frozenset(block for child in affected_children for block in new_graph.node[child]['blocks'])
        inherited_children = set(y for x in affected_children for y in new_graph.neighbors(x))
        inherited_children.remove(self.head_node)

        new_graph.remove_nodes_from(affected_children)
        for child in inherited_children:
            new_graph.add_edge(self.head_node, child)
        new_graph.node[self.head_node]['color'] = move
        new_graph.node[self.head_node]['blocks'] = gained_blocks.union(new_graph.node[self.head_node]['blocks'])
        return self.__class__(self.width, self.height, self.num_colors, last_move=move, parent=self,
                              num_moves=self.num_moves + 1, head_node=self.head_node, initial_graph=new_graph)

    def is_goal(self):
        return self.graph.number_of_nodes() == 1

    def valid_actions(self):
        return set(self.graph.node[x]['color'] for x in self.graph.neighbors(self.head_node))

    def draw_graph(self):
        plt.imshow(py.array(
            map(lambda x: map(lambda y: mplc.colorConverter.to_rgb(colord[y]), x), self.create_grid(self.graph))),
                   interpolation='nearest')
        plt.show()

    def write_graph_to_file(self, path):
        graph = nx.Graph()
        for node in self.graph.nodes(data=True):
            new_node = deepcopy(node)
            new_node[1]['blocks'] = list(new_node[1]['blocks'])
            graph.add_node(*new_node)
        graph.add_edges_from(self.graph.edges())
        json.dump(json_graph.node_link_data(graph), open(path, 'w'))

    def h_score(self):
        if self.estimated_moves_to_goal is None:
            self.estimated_moves_to_goal = \
                max(nx.single_source_shortest_path_length(self.graph, self.head_node).items(), key=lambda x: x[1])[1]
        return self.estimated_moves_to_goal

    def g_score(self):
        return self.num_moves

    def f_score(self):
        return self.g_score() + self.h_score()

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __cmp__(self, other):
        f1 = self.f_score()
        f2 = other.f_score()
        if f1 < f2:
            return -1
        elif f1 == f2:
            return 0
        else:
            return 1


class RedundantCheckingState(_State):
    def __init__(self, width, height, num_colors, last_move=None, parent=None, num_moves=0, head_node=None,
                 initial_values=None, initial_graph=None):
        _State.__init__(self, width, height, num_colors, last_move, parent, num_moves, head_node, initial_values,
                        initial_graph)
        self.id = hash(self.graph.node[self.head_node]['blocks'])


class State(_State):
    def __init__(self, width, height, num_colors, last_move=None, parent=None, num_moves=0, head_node=None,
                 initial_values=None,
                 initial_graph=None):
        _State.__init__(self, width, height, num_colors, last_move, parent, num_moves, head_node, initial_values,
                        initial_graph)
        self.id = rand.getrandbits(64)
