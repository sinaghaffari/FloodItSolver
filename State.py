import uuid

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
from numpy import random, array

__author__ = 'sina'

colord = {
    0: '#ff0000',
    1: '#00ff00',
    2: '#0000ff',
    3: '#ffff00',
    4: '#ff00ff',
    5: '#00ffff'
}


class State:
    def __init__(self, width, height, num_colors, last_move, num_moves=0, initial_values=None, initial_graph=None):
        self.last_move = last_move
        self.num_moves = num_moves
        self.width = width
        self.height = height
        self.num_colors = num_colors
        if initial_values is None and initial_graph is None:
            self.values = random.randint(num_colors, size=(height, width))
            # print "Initial Values:"
            # print self.values
            self.graph, self.graph_map = self.create_graph(self.values)
        elif initial_values is None and initial_graph is not None:
            self.graph = initial_graph
            self.values, self.graph_map = self.create_grid(self.graph)
        elif initial_values is not None and initial_graph is None:
            self.values = initial_values
            self.graph, self.graph_map = self.create_graph(self.values)
        self.moves = 0
        self._id = hash(frozenset(self.graph.node[self.graph_map[0][0]]['blocks'] + [self.moves]))
        self._hscore = None

        # d = json_graph.node_link_data(self.graph)
        # json.dump(d, open('static/force.json', 'w'))

    def create_grid(self, graph):
        values = array([[0] * self.width] * self.height)
        graph_map = array([[''] * self.width] * self.height, dtype=object)
        for node in graph.nodes(data=True):
            for block in node[1]['blocks']:
                x = block // self.width
                y = block % self.width
                values[x][y] = node[1]['color']
                graph_map[x][y] = node[0]
        return array(values), graph_map

    def create_graph(self, values):
        color_map = array([[''] * self.width] * self.height, dtype=object)
        graph = nx.Graph()

        def flood_fill(x, y, value):
            initial_value = values[y][x]
            attr_dict = {'blocks': [], 'color': initial_value}
            if x == 0 and y == 0:
                attr_dict['root'] = True
            graph.add_node(value, attr_dict=attr_dict)
            visited = []
            queue = [(y, x)]
            while len(queue) != 0:
                current = queue.pop()
                visited.append(current)
                color_map[current[0]][current[1]] = value
                graph.node[value]['blocks'].append(current[0] * self.width + current[1])
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

        for i in range(len(values)):
            for j in range(len(values[i])):
                if color_map[i][j] == '':
                    flood_fill(j, i, str(uuid.uuid4()))
        return graph, color_map

    def successors(self):
        return [self.do_move(x) for x in self.valid_actions()]

    def do_move(self, move):
        new_graph = self.graph.copy()
        affected_children = filter(lambda x: new_graph.node[x]['color'] == move, new_graph.neighbors(self.head_node()))
        gained_blocks = [block for child in affected_children for block in new_graph.node[child]['blocks']]
        inherited_children = set(y for x in affected_children for y in new_graph.neighbors(x))
        inherited_children.remove(self.head_node())

        new_graph.remove_nodes_from(affected_children)
        for child in inherited_children:
            new_graph.add_edge(self.head_node(), child)
        new_graph.node[self.head_node()]['color'] = move
        new_graph.node[self.head_node()]['blocks'].extend(frozenset(gained_blocks))
        return State(self.width, self.height, self.num_colors, move, self.num_moves + 1, initial_graph=new_graph)

    def valid_actions(self):
        return set(self.graph.node[x]['color'] for x in self.graph.neighbors(self.head_node()))

    def draw_graph(self):
        plt.imshow(array(map(lambda x: map(lambda y: mplc.colorConverter.to_rgb(colord[y]), x), self.values)),
                   interpolation='nearest')
        plt.show()

    def head_node(self):
        return self.graph_map[0][0]

    def hscore(self):
        if self._hscore is None:
            self._hscore = \
            max(nx.single_source_shortest_path_length(self.graph, self.head_node()).items(), key=lambda x: x[1])[1]
        return self._hscore

    def fscore(self):
        return self.num_moves + self.hscore()

    def __hash__(self):
        return self._id

    def __eq__(self, other):
        return type(other) is State and self._id == other._id

    def __cmp__(self, other):
        f1 = self.fscore()
        f2 = other.fscore()
        if f1 < f2:
            return -1
        elif f1 == f2:
            return 0
        else:
            return 1