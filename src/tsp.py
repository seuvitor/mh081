from numpy import *
import random
from os.path import basename, splitext
import copy
from bisect import bisect_left


class TSP():
    
    
    def get_problem_optimization_sense(self):
        MIN = -1
        MAX = 1
        
        return MIN
    
    
    def get_instances_dir(self):
        return '../tsp_instances/'
    
    
    def get_problem_name(self):
        return 'TSP'
    
    
    def read_instance_data(self, file):
        # Get num of vertices
        line = file.readline()
        while not line.startswith('DIMENSION'):
            line = file.readline()
        
        num_vertices = eval(line.split().pop())
        
        # Skip lines 
        while not line.startswith('NODE_COORD_SECTION'):
            line = file.readline()
        
        # Get cities coordinates from the input file
        coordinates = []
        line = file.readline()
        while not line.startswith('EOF'):
            [id, x, y] = line.split()
            coordinates.append((float(x), float(y)))
            line = file.readline()
        
        D = zeros((num_vertices, num_vertices), dtype=int)
        
        # Calculate distances between cities
        for u in range(num_vertices):
            for v in range(num_vertices):
                (x_u, y_u) = coordinates[u]
                (x_v, y_v) = coordinates[v]
                D_uv = round(sqrt(((x_v - x_u)**2) + ((y_v - y_u)**2)))
                D[u,v] = D_uv
                D[v,u] = D_uv
        
        instance_data = (num_vertices, coordinates, D)
        return instance_data
    
    
    def read_problem_set_file(self, file_path):
        (problem_set_name, ext) = splitext(basename(file_path))
        
        file = open(file_path, 'r')
        
        instance_name = problem_set_name
        instance_data = self.read_instance_data(file)
        (num_vertices, coordinates, D) = instance_data
        
        instance = TSPInstance(self, instance_name, num_vertices, coordinates, D)
        
        return [instance]
    
    
    def get_opt_value(self, instance_name):
        map = {'a280':      2579.0,\
               'ali535':    202310.0,\
               'att48':     10628.0,\
               'att532':    27686.0,\
               'bayg29':    1610.0,\
               'bays29':    2020.0,\
               'berlin52':  7542.0,\
               'bier127':   118282.0,\
               'brazil58':  25395.0,\
               'brd14051':  468942.0,\
               'brg180':    1950.0,\
               'burma14':   3323.0,\
               'ch130':     6110.0,\
               'ch150':     6528.0,\
               'd198':      15780.0,\
               'd493':      35002.0,\
               'd657':      48912.0,\
               'd1291':     50801.0,\
               'd1655':     62128.0,\
               'd2103':     79952.0,\
               'd18512':    644650.0,\
               'dantzig42': 699.0,\
               'dsj1000':   18659688.0,\
               'eil51':     426.0,\
               'eil76':     538.0,\
               'fl417':     11861.0,\
               'fl1400':    20127.0,\
               'fl1577':    22204.0,\
               'fl3795':    28723.0,\
               'fnl4461':   182566.0,\
               'fri26':     937.0,\
               'gil262':    2378.0,\
               'gr17':      2085.0,\
               'gr21':      2707.0,\
               'gr24':      1272.0,\
               'gr48':      5046.0,\
               'gr96':      55209.0,\
               'gr120':     6942.0,\
               'gr137':     69853.0,\
               'gr202':     40160.0,\
               'gr229':     134602.0,\
               'gr431':     171414.0,\
               'gr666':     294358.0,\
               'hk48':      11461.0,\
               'kroA100':   21282.0,\
               'kroB100':   22141.0,\
               'kroC100':   20749.0,\
               'kroD100':   21294.0,\
               'kroE100':   22068.0,\
               'kroA150':   26524.0,\
               'kroB150':   26130.0,\
               'kroA200':   29368.0,\
               'kroB200':   29437.0,\
               'lin105':    14379.0,\
               'lin318':    42029.0,\
               'linhp318':  41345.0,\
               'nrw1379':   56638.0,\
               'p654':      34643.0,\
               'pa561':     2763.0,\
               'pcb442':    50778.0,\
               'pcb1173':   56892.0,\
               'pcb3038':   137694.0,\
               'pla7397':   23260728.0,\
               'pla33810':  65913275.0,\
               'pla85900':  141904862.0,\
               'pr76':      108159.0,\
               'pr107':     44303.0,\
               'pr124':     59030.0,\
               'pr136':     96772.0,\
               'pr144':     58537.0,\
               'pr152':     73682.0,\
               'pr226':     80369.0,\
               'pr264':     49135.0,\
               'pr299':     48191.0,\
               'pr439':     107217.0,\
               'pr1002':    259045.0,\
               'pr2392':    378032.0,\
               'rat99':     1211.0,\
               'rat195':    2323.0,\
               'rat575':    6773.0,\
               'rat783':    8806.0,\
               'rd100':     7910.0,\
               'rd400':     15281.0,\
               'rl1304':    252948.0,\
               'rl1323':    270199.0,\
               'rl1889':    316536.0,\
               'rl5915':    565040,\
               'rl5934':    554070.0,\
               'rl11849':   920847.0,\
               'si175':     21407.0,\
               'si535':     48450.0,\
               'si1032':    92650.0,\
               'st70':      675.0,\
               'swiss42':   1273.0,\
               'ts225':     126643.0,\
               'tsp225':    3919.0,\
               'u159':      42080.0,\
               'u574':      36905.0,\
               'u724':      41910.0,\
               'u1060':     224094.0,\
               'u1432':     152970.0,\
               'u1817':     57201.0,\
               'u2152':     64253.0,\
               'u2319':     234256.0,\
               'ulysses16': 6859.0,\
               'ulysses22': 7013.0,\
               'usa13509':  19947008.0,\
               'vm1084':    239297.0,\
               'vm1748':    336556.0}
        
        if not instance_name in map:
            return None
        else:
            return map[instance_name]


class TSPInstance():
    
    
    def __init__(self, problem, name, num_vertices, coordinates, D):
        self.problem = problem
        self.name = name
        self.num_vertices = num_vertices
        self.coordinates = coordinates
        self.D = D
    
    
    def get_problem_size(self):
        return self.num_vertices
    
    
    def generate_random_solution(self):
        tour = range(0, self.num_vertices)
        random.shuffle(tour)
        
        solution = TSPSolution(self, tour)
        return solution
    
    
    def generate_greedy_randomized_solution(self, k):
        remaining_vertices = range(0, self.num_vertices)
        head = tail = remaining_vertices.pop(0)
        
        # Start solution with the first vertex
        tour = [head]
        
        # At each iteration, add one of the k-nearest vertices to the solution
        while len(remaining_vertices) > 0:
            
            candidates_dists = []
            candidates_indices = []
            
            # Mount lists (of distances and indices) of the k-nearest vertices
            for i in range(len(remaining_vertices)):
                v = remaining_vertices[i]
                dist = min(self.D[head, v], self.D[tail, v])
                
                # Find place to insert, keeping the list sorted by distances
                insertion_point = bisect_left(candidates_dists, dist)
                if (insertion_point < k):
                    candidates_dists.insert(insertion_point, dist)
                    candidates_indices.insert(insertion_point, i)
                
                # There must be at most k candidates
                if len(candidates_dists) > k:
                    candidates_dists.pop(k)
                    candidates_indices.pop(k)
            
            # Choose any of the k-nearest vertices
            nearest_vertex_index = random.choice(candidates_indices)
            
            # Remove from the remaining vertices list
            nearest_vertex = remaining_vertices.pop(nearest_vertex_index)
            
            # Decide if the new vertex goes to the head or tail of the solution
            if self.D[head, nearest_vertex] < self.D[tail, nearest_vertex]:
                tour.insert(0, nearest_vertex)
                head = nearest_vertex
            else:
                tour.append(nearest_vertex)
                tail = nearest_vertex
        
        solution = TSPSolution(self, tour)
        return solution
    
    
    def generate_all_moves(self):
        size = self.num_vertices
        
        moves = []
        
        for i in range(0, (size - 2)):
            for k in range(2, (size - max(1, i))): # Avoid equivalent moves
                j = i + k
                moves.append((i, j))
        
        random.shuffle(moves)
        return moves


class TSPSolution():
    
    
    def __init__(self, instance, tour):
        self.instance = instance
        self.tour = tour
    
    
    def __str__(self):
        tour_str = ''
        for i in range(len(self.tour)):
            tour_str += str(self.tour[i]) + ','
        return tour_str
    
    
    def draw_solution(self):
        from Tkinter import *
        root = Tk()
        
        (screen_width, screen_height) = (640, 480)
        canvas = Canvas(root, width=screen_width, height=screen_height, bg='white')
        
        size = self.instance.num_vertices
        for i in range(size):
            (x_u, y_u) = self.instance.coordinates[self.tour[i]]
            (x_v, y_v) = self.instance.coordinates[self.tour[(i + 1) % size]]
            canvas.create_line((x_u, y_u, x_v, y_v), fill='black')
        
        # Fit the drawing to the screen size
        (min_x, min_y, max_x, max_y) = canvas.bbox(ALL)
        x_scale = float(screen_width) / float(max_x - min_x)
        y_scale = float(screen_height) / float(max_y - min_y)
        min_scale = min(x_scale, y_scale)
        canvas.scale(ALL, 0, 0, min_scale/1.5, min_scale/1.5)
        
        canvas.pack()
        root.mainloop()
    
    
    def calculate_value(self):
        value = 0
        size = self.instance.num_vertices
        
        # Add weights of edges linking consecutive vertices in the tour
        for i in range(size - 1):
            value += self.instance.D[self.tour[i], self.tour[i + 1]]
        
        # Add the weight of the returning edge
        value += self.instance.D[self.tour[0], self.tour[size - 1]]
        
        return value
    
    
    def calculate_move_delta(self, (i, j)):
        size = self.instance.num_vertices
        
        a, b = self.tour[i], self.tour[(i + 1) % size]
        d, c = self.tour[j], self.tour[(j + 1) % size]
        delta = self.instance.D[a, d] + self.instance.D[b, c]\
                - self.instance.D[a, b] - self.instance.D[d, c]
        return delta
    
    
    def generate_random_move(self):
        size = self.instance.num_vertices
        
        i = random.randint(0, (size - 3))
        k = random.randint(2, (size - max(2, i + 1))) # Avoid equivalent moves
        j = i + k
        delta = self.calculate_move_delta((i, j))
        return ((i, j), delta)
    
    
    def apply_move(self, (i, j)):
        
        # If needed, swap the indices, so that the subtour is
        # within the boundaries of the sequence
        if i > j:
            (i, j) = (j, i)
            
        subtour = self.tour[(i + 1):(j + 1)]
        subtour.reverse()
        self.tour[(i + 1):(j + 1)] = subtour
    
    
    def is_tabu(self, tabu_list, (i, j)):
        size = self.instance.num_vertices
        
        a, b = self.tour[i], self.tour[(i + 1) % size]
        d, c = self.tour[j], self.tour[(j + 1) % size]
        
        # This movement is tabu if it is trying to construct an edge that was
        # recently removed, i.e. that is still in the tabu list
        for tabu in tabu_list:
            (e1, e2) = tabu
            if e1 == (a, d) or e1 == (d, a) or e2 == (a, d) or e2 == (d, a)\
                    or e1 == (b, c) or e1 == (c, b) or e2 == (b, c) or e2 == (c, b):
                return True
        return False
    
    
    def append_tabu(self, tabu_list, (i, j)):
        size = self.instance.num_vertices
        
        a, b = self.tour[i], self.tour[(i + 1) % size]
        d, c = self.tour[j], self.tour[(j + 1) % size]
        
        # Append removed edges to the tabu list to avoid their early reconstruction
        tabu_list.append(((a, b), (c, d)))
