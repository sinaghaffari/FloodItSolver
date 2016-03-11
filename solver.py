import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mplc
from networkx.readwrite import json_graph
from numpy import random, array, vectorize
import uuid

n = 12
m = 11
c = 6


class State:
    def __init__(self, initial_values, width, height, num_colors):
        self.width = width
        self.height = height
        self.num_colors = num_colors
        self.values = initial_values
        self.moves = 0
        self.graph, self.graph_map = self.create_graph(self.values)
        d = json_graph.node_link_data(self.graph)
        json.dump(d, open('static/force.json', 'w'))

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
                graph.node[value]['blocks'].append(current)
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
        root = color_map[0][0]
        distances = sorted(nx.single_source_shortest_path_length(graph, root).items(), key=lambda x: x[1], reverse=True)
        print distances[0]
        furthest = map(lambda y: y[0], filter(lambda x: x[1] == distances[0][1], distances))
        print furthest

        paths = []
        for t in furthest:
            paths.extend(nx.all_shortest_paths(graph, source=root, target=t))
        for p in paths:
            path = list(p)
            for i in range(len(path) - 1):
                graph.edge[path[i]][path[i + 1]]['shortest'] = True
        return graph, color_map

    def draw_graph(self):
        plt.imshow(array(map(lambda x: map(lambda y: mplc.colorConverter.to_rgb(colord[y]), x), self.values)),
                   interpolation='nearest')
        plt.show()


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
s = State(random.randint(c,  size=(m, n)), n, m, c)

colord = {
    0: '#ff0000',
    1: '#00ff00',
    2: '#0000ff',
    3: '#ffff00',
    4: '#ff00ff',
    5: '#00ffff'
}

s.draw_graph()
