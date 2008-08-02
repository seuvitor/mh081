from numpy import *
import random
import copy
from os.path import basename, splitext


class GCP():
    
    
    def get_problem_optimization_sense(self):
        MIN = -1
        MAX = 1
        
        return MIN
    
    
    def get_instances_dir(self):
        return '../gcp_instances/'
    
    
    def get_problem_name(self):
        return 'GCP'
    
    
    def read_instance_data(self, file):
        line = file.readline()
        while (line.split()[0] != 'p'): line = file.readline() # Skip comments

        # Parse number of vertices and edges
        [p, edge, num_vertices, num_edges] = line.split()
        num_vertices, num_edges = eval(num_vertices), eval(num_edges)
        
        # Create empty adjacency lists
        gamma = [[] for i in range(num_vertices)]
        
        # Parse edges, filling adjacency lists accordingly
        line = file.readline()
        while line != None and line.strip() != '':
            if (line.split()[0] == 'e'):
                [e, u, v] = line.split()
                u, v = (eval(u) - 1), (eval(v) - 1)
                gamma[u].append(v)
                gamma[v].append(u)
            
            line = file.readline()
        
        instance_data = (num_vertices, gamma)
        return instance_data
    
    
    def read_problem_set_file(self, file_path):
        (problem_set_name, ext) = splitext(basename(file_path))
        
        file = open(file_path, 'r')
        
        instance_name = problem_set_name
        instance_data = self.read_instance_data(file)
        (num_vertices, gamma) = instance_data
        
        instance = GCPInstance(self, instance_name, num_vertices, gamma)
        
        return [instance]
    
    
    def get_opt_value(self, instance_name):
        map = {'flat1000_50_0': 50,\
               'flat1000_60_0': 60,\
               'flat1000_76_0': 76,\
               'flat300_20_0': 20,\
               'flat300_26_0': 26,\
               'flat300_28_0': 28,\
               'le450_15a': 15,\
               'le450_15b': 15,\
               'le450_15c': 15,\
               'le450_15d': 15,\
               'le450_25a': 25,\
               'le450_25b': 25,\
               'le450_25c': 25,\
               'le450_25d': 25,\
               'le450_5a': 5,\
               'le450_5b': 5,\
               'le450_5c': 5,\
               'le450_5d': 5}
        
        if not instance_name in map:
            return None
        else:
            return map[instance_name]


class GCPInstance():
    
    
    def __init__(self, problem, name, num_vertices, gamma):
        self.problem = problem
        self.name = name
        self.num_vertices = num_vertices
        self.gamma = gamma
    
    
    def get_tabu_tenure(self):
        return self.num_vertices / 8
    

    def get_expected_num_tabu_iterations(self):
        return self.num_vertices * 100
    

    def get_expected_num_sa_iterations(self):
        return self.num_vertices * 5000
    
    
    def min_feasible_color(self, coloring, count_adj_colors, vertex,
                           forbiden = -1):
        color = 0 if (forbiden != 0) else 1
        
        while count_adj_colors[vertex, color] > 0:
            color += 1
            if (color == forbiden): color += 1
                
        return color
    
    def generate_random_solution(self):
        coloring = ones((self.num_vertices), dtype=int) * -1
        count_adj_colors = zeros((self.num_vertices, self.num_vertices),
                                 dtype=int)
        
        # Get random permutation of vertices
        uncolored = range(self.num_vertices)
        random.shuffle(uncolored)
        
        # Color each vertex with the minimum feasible color
        for u in uncolored:
            color = self.min_feasible_color(coloring, count_adj_colors, u)
            coloring[u] = color
            for v in self.gamma[u]:
                count_adj_colors[v, color] += 1
        
        solution = GCPSolution(self, coloring, count_adj_colors)
        return solution
    
    
    def generate_greedy_randomized_solution(self, k):
        coloring = ones((self.num_vertices), dtype=int) * -1
        count_adj_colors = zeros((self.num_vertices, self.num_vertices),
                                 dtype=int)
        
        # Get random permutation of vertices
        uncolored = range(self.num_vertices)
        random.shuffle(uncolored)
        
        P_0 = k * 0.03
        size_uncolored = len(uncolored)
        
        # Color each vertex with the minimum feasible color
        for i in range(size_uncolored):
            u = uncolored[i]
            
            color = self.min_feasible_color(coloring, count_adj_colors, u)
            coloring[u] = color
            
            # With a positive probability, use another color
            P = P_0 * (size_uncolored - i) / size_uncolored
            if random.random() > (1.0 - P):
                color = self.min_feasible_color(coloring, count_adj_colors,
                                                u, coloring[u])
                coloring[u] = color
            
            # Update count of adjacent colors
            for v in self.gamma[u]:
                count_adj_colors[v, color] += 1
        
        solution = GCPSolution(self, coloring, count_adj_colors)
        return solution
    
    
    def generate_all_moves(self):
        moves = range(self.num_vertices)
        random.shuffle(moves)
        return moves
    
    
class GCPSolution():
    
    
    def __init__(self, instance, coloring, count_adj_colors):
        self.instance = instance
        self.coloring = coloring
        self.count_adj_colors = count_adj_colors
    
    
    def __copy__(self):
        return GCPSolution(self.instance, self.coloring.copy(),
                           self.count_adj_colors.copy())
    
    
    def __deepcopy__(self):
        return self.__copy__()
    
    
    def __str__(self):
        coloring_str = ''
        for color in self.coloring:
            coloring_str += str(color) + ','
        return coloring_str
    
    
    def draw_solution(self):
        return
    
    
    def calculate_value(self):
        """ Minimizing the objective function favors large color classes:
            f(s) = - \sum_{i=1}^{K} {|C_i|^2}
        """
        value = 0
        classes_sizes = bincount(self.coloring)
        for class_size in classes_sizes:
            value = value - (class_size ** 2)
        return value
    
    
    def calculate_move_delta(self, vertex):
        delta = 0 
        
        old_color = self.coloring[vertex]
        new_color = self.instance.min_feasible_color(self.coloring, \
                self.count_adj_colors, vertex, old_color);

        classes_sizes = bincount(self.coloring)
        old_color_count = classes_sizes[old_color]
        
        new_color_count = 0
        try:
            new_color_count = classes_sizes[new_color]
        except:
            new_color_count = 0 # Color was not being used.
        
        delta = delta + (old_color_count ** 2) \
                      - ((old_color_count - 1) ** 2)

        delta = delta + (new_color_count ** 2) \
                      - ((new_color_count + 1) ** 2)
        
        return delta
    
    
    def generate_random_move(self):
        # Get random index for alternating binary value
        vertex = random.randint(0, (self.instance.num_vertices - 1))
        
        delta = self.calculate_move_delta(vertex)
        return (vertex, delta)
    
    
    def apply_move(self, vertex):
        old_color = self.coloring[vertex]
        new_color = self.instance.min_feasible_color(self.coloring, \
                self.count_adj_colors, vertex, old_color);
        
        self.coloring[vertex] = new_color
        
        # Update count of adjacent colors
        for v in self.instance.gamma[vertex]:
            self.count_adj_colors[v, old_color] -= 1
            self.count_adj_colors[v, new_color] += 1
    
    
    def is_tabu(self, tabu_list, vertex):
        return (vertex in tabu_list)
    
    
    def append_tabu(self, tabu_list, vertex):
        # Add the vertex whose color changed to the tabu list
        # to avoid changing its color too early
        tabu_list.append(vertex)
