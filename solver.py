import time
import json
import uuid

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
from networkx.readwrite import json_graph
from numpy import random, array
from sortedcontainers import SortedSet

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
            print "Initial Values:"
            print self.values
            self.graph, self.graph_map = self.create_graph(self.values)
        elif initial_values is None and initial_graph is not None:
            self.graph = initial_graph
            self.values, self.graph_map = self.create_grid(self.graph)
        elif initial_values is not None and initial_graph is None:
            self.values = initial_values
            self.graph, self.graph_map = self.create_graph(self.values)
        self.moves = 0
        self._id = hash(frozenset(self.graph.node[self.graph_map[0][0]]['blocks']))
        self.fscore = max(nx.single_source_shortest_path_length(self.graph, self.head_node()).items(), key=lambda x: x[1])[1]

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

    def __hash__(self):
        return self._id

    def __eq__(self, other):
        return type(other) is State and self._id == other._id

    def __cmp__(self, other):
        if self.fscore < other.fscore:
            return -1
        elif self.fscore == other.fscore:
            return 0
        else:
            return 1


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
            print "Nodes searched =", len(closed_set)
            print "Nodes to be searched =", len(open_set)
            print "Time Taken =", (time.time() - start_time)
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
    open_set = SortedSet()
    open_set.add(start)
    camefrom = dict()

    graph = nx.Graph()
    graph.add_node(hash(start), status="open", start=True)
    while len(open_set) != 0:
        current = open_set.pop(0)
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
                open_set.add(successor)
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

n = 20  # width
m = 20  # height
c = 6  # number of colors

# initial state
s = State(n, m, c, None, initial_values=a)

# output the state as a json graph.
d = json_graph.node_link_data(s.graph)
json.dump(d, open('static/force.json', 'w'))

# run search.
ngraph, path_moves = a_star(s)

# output the search as a json graph.
ngraph.node[hash(path_moves[-1])]['end'] = True
for i in range(len(path_moves) - 1):
    ngraph.edge[hash(path_moves[i])][hash(path_moves[i + 1])]['optimal'] = True
json.dump(json_graph.node_link_data(ngraph), open('static/force2.json', 'w'))

# Print the grid after each optimal move.
for i, move in enumerate(path_moves):
    print "Move", i, ":", move.last_move
    print move.values

# Print the optimal number of moves and what each move is.
print len(path_moves) - 1, "-", map(lambda x: x.last_move, path_moves)[1:]
