from numpy import *
import random
from os.path import basename, splitext
import copy

class DSP():
    
    
    def get_problem_optimization_sense(self):
        MIN = -1
        MAX = 1
        
        return MIN
    
    
    def get_instances_dir(self):
        return '../dsp_instances/'
    
    
    def get_problem_name(self):
        return 'DSP'
    
    
    def read_instance_data(self, file):
        # Get num of vertices
        line = file.readline()

        # Parse number of vertices
        num_vertices, num_neighbors = line.split()
        num_vertices, num_neighbors = eval(num_vertices), eval(num_neighbors)
        
        gamma = []
        
        # Parse vehicles capacity
        for u in range(num_vertices):
            line = file.readline()
            # Subtract 1 to convert to 0-indexed
            gamma_u = [eval(v) - 1 for v in line.split()]
            gamma.append(gamma_u)
            
        instance_data = (num_vertices, num_neighbors, gamma)
        return instance_data
    
    
    def read_problem_set_file(self, file_path):
        (problem_set_name, ext) = splitext(basename(file_path))
        
        file = open(file_path, 'r')
        
        instance_name = problem_set_name
        instance_data = self.read_instance_data(file)
        (num_vertices, num_neighbors, gamma) = instance_data
        
        instance = DSPInstance(self, instance_name, num_vertices,
                               num_neighbors, gamma)
        
        return [instance]
    
    
    def get_opt_value(self, instance_name):
        map = {'dom-set-1-73' : 73,
               'dom-set-2-186' : 186}
        map = {}

        
        if not instance_name in map:
            return None
        else:
            return map[instance_name]


class DSPInstance():
    
    
    def __init__(self, problem, name, num_vertices, num_neighbors, gamma):
        self.problem = problem
        self.name = name
        self.num_vertices = num_vertices
        self.num_neighbors = num_neighbors
        self.gamma = gamma
        
        max_uncovercount_penalty = int(self.num_neighbors \
                                   * (((self.num_neighbors - 1) ** 2) \
                                      + ((self.num_neighbors - 2) ** 2)))
        
        self.cardinality_penalty = int(max_uncovercount_penalty * 1.1)
        self.uncovered_penalty = int(max_uncovercount_penalty * 1.11)
        
    
    
    def get_problem_size(self):
        return self.num_vertices
    

    def get_tabu_tenure(self):
        return self.num_vertices / 2
    

    def get_expected_num_tabu_iterations(self):
        return self.num_vertices * 20
    

    def get_expected_num_sa_iterations(self):
        return self.num_vertices * 2500#15000
    
    
    def generate_random_solution(self):
        vars = zeros((self.num_vertices), dtype=int)

        for u in range(self.num_vertices):
            vars[u] = (1 if (random.random() > 0.8) else 0)
        
        solution = DSPSolution(self, vars)
        return solution
    
    
    def generate_greedy_randomized_solution(self, k):
        vars = zeros((self.num_vertices), dtype=int)
        
        num_covered_neighbors = [0 for i in range(self.num_vertices)]
        uncovered_vertices = set(range(self.num_vertices))
        
        for i in range(self.num_vertices):
            
            if len(uncovered_vertices) < 1: break
            P_skip_best = 0.1 * k * len(uncovered_vertices) / self.num_vertices
            
            best_vertex = None
            best_vertex_count = None
            for u in uncovered_vertices:
                if best_vertex == None or best_vertex_count > num_covered_neighbors[u]:
                    if random.random() > P_skip_best:
                        best_vertex = u
                        best_vertex_count = num_covered_neighbors[u]
            
            if best_vertex == None: continue
            
            vars[best_vertex] = 1

            # Remove neighbors (and itself) from uncovered_vertices
            for v in self.gamma[best_vertex]:
                if v in uncovered_vertices:
                    uncovered_vertices.discard(v)
                    
                    # Update counters of covered neighbors
                    for w in self.gamma[v]:
                        num_covered_neighbors[w] += 1
        
        solution = DSPSolution(self, vars)
        return solution
    
    
    def generate_all_moves(self):
        return range(self.num_vertices)


class DSPSolution():
    
    
    def __init__(self, instance, vars):
        self.instance = instance
        self.vars = vars
        self.cover_count = ones((self.instance.num_vertices), dtype=int) * self.instance.num_neighbors
        for u in range(self.instance.num_vertices):
            if self.vars[u] == 1:
                for v in self.instance.gamma[u]:
                    self.cover_count[v] -= 1
        
    
    
    def __copy__(self):
        import copy
        return DSPSolution(self.instance,
                           copy.deepcopy(self.vars))
    
    
    def __deepcopy__(self):
        return self.__copy__()
    
    
    def __str__(self):
        vars_str = ''
        for var in self.vars:
            vars_str += str(var) + ','
        return vars_str
    
    
    def draw_solution(self):
        return
    
    
    def calculate_report_value(self):
        value = 0
        for u in range(self.instance.num_vertices):
            value += self.vars[u]
            if self.cover_count[u] == self.instance.num_neighbors:
                return 'INF'
        return value
    
    
    def calculate_value(self):
        value = 0
        
        for u in range(self.instance.num_vertices):
            value += self.vars[u] * self.instance.cardinality_penalty
            
            # Penalize if vertex is uncovered
            if self.cover_count[u] == self.instance.num_neighbors:
                value += self.instance.uncovered_penalty
                value += (self.instance.num_neighbors - 1) ** 2
            else:
                value += self.cover_count[u] ** 2
        
        return value
    
    
    def calculate_move_delta(self, u):
        move_delta = 0
        
        num_neighbors = self.instance.num_neighbors
        
        if self.vars[u] == 0:
            # Cardinality of the solution set is incremented
            move_delta += 1 * self.instance.cardinality_penalty
            
            # Remove penalization for all vertices that become covered
            for v in self.instance.gamma[u]:
                if self.cover_count[v] == self.instance.num_neighbors:
                    move_delta -= self.instance.uncovered_penalty
                else:
                    move_delta -= (self.cover_count[v] ** 2) - ((self.cover_count[v] - 1) ** 2)
        else:
            # Cardinality of the solution set is decremented
            move_delta -= self.instance.cardinality_penalty
            
            # Penalize for all vertices that become uncovered
            for v in self.instance.gamma[u]:
                if self.cover_count[v] == (self.instance.num_neighbors - 1):
                    move_delta += self.instance.uncovered_penalty
                else:
                    move_delta += ((self.cover_count[v] + 1) ** 2) - (self.cover_count[v] ** 2)
        
        return move_delta
    
    
    def generate_random_move(self):
        # Get random vertex to switch value
        u = random.randint(0, (self.instance.num_vertices - 1))
        
        delta = self.calculate_move_delta(u)
        return (u, delta)
    
    
    def apply_move(self, u):
        estimated_delta = self.calculate_move_delta(u)
        value_befor = self.calculate_value()
        
        if self.vars[u] == 0:
            # Insert u into the solution set
            self.vars[u] = 1
            
            # Increment cover count of neighbor vertices
            for v in self.instance.gamma[u]:
                self.cover_count[v] -= 1
        else:
            # Remove u from the solution set
            self.vars[u] = 0
            
            # Decrement cover count of neighbor vertices
            for v in self.instance.gamma[u]:
                self.cover_count[v] += 1
        
        value_after = self.calculate_value()
        if value_after - value_befor != estimated_delta:
            print value_after, '-', value_befor, '!=', estimated_delta
    
    
    def polish(self):
        """ Perform a local search to improve the solution. By construction,
            all local optima are feasible, so polishing can be
            applied to any unfeasible solution to render it feasible. 
        """
        
        # Generate all possible moves
        moves = self.instance.generate_all_moves()
        
        # Start local search
        improving = True
        while improving:
            improving = False
            for move in moves:
                delta = self.calculate_move_delta(move)
                
                # If the neighbor solution is better, move to it
                if delta < 0:
                    self.apply_move(move)
                    improving = True
                    break
    
    
    def is_tabu(self, tabu_list, u):
        return ((u, self.vars[u]) in tabu_list)# or \
        #        (len(tabu_list) >= 3 and (u, (1 - self.vars[u])) in tabu_list[-2:])
    
    
    def append_tabu(self, tabu_list, u):
        # Add the vertex whose value changed and its state to the tabu list
        # to avoid reseting it too early
        if random.random() < 0.01:
            u = random.randint(0, (self.instance.num_vertices - 1))
        tabu_list.append((u, self.vars[u]))
