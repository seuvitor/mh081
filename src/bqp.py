from numpy import *
import random
from os.path import basename, splitext
import copy


class BQP():
    
    
    def get_problem_optimization_sense(self):
        MIN = -1
        MAX = 1
        
        return MAX
    
    
    def get_instances_dir(self):
        return '../bqp_instances/'
    
    
    def get_problem_name(self):
        return 'UBQP'
    
    
    def read_instance_data(self, file):
        line = file.readline()
        [num_vars, num_non_zero] = line.split()
        num_vars, num_non_zero = eval(num_vars), eval(num_non_zero)
        
        # Create n*n matrix filled with zeroes
        Q = zeros((num_vars, num_vars), dtype=int)
        
        for i in range(num_non_zero):
            line = file.readline()
            [i, j, q_ij] = line.split()
            i, j, q_ij = eval(i), eval(j), eval(q_ij)
            
            # Decrement 1-indexed indices for using in a 0-indexed array
            i -= 1
            j -= 1
            
            Q[i,j] = q_ij
            Q[j,i] = q_ij
        
        instance_data = (num_vars, Q)
        return instance_data
    
    
    def read_problem_set_file(self, file_path):
        (problem_set_name, ext) = splitext(basename(file_path))
        
        file = open(file_path, 'r')
        
        line = file.readline()
        num_problems = eval(line.strip())
        
        instances_list = []
        
        instance_count = 1
        
        for i in range(num_problems):
            instance_name = problem_set_name + ' (' + str(instance_count) + ')'
            
            instance_data = self.read_instance_data(file)
            (num_vars, Q) = instance_data
            
            instance = BQPInstance(self, instance_name, num_vars, Q)
            instances_list.append(instance)
            
            instance_count += 1
        
        return instances_list
    
    
    def get_opt_value(self, instance_name):
        map = {'bqp50 (1)': 2098,\
               'bqp50 (2)': 3702,\
               'bqp50 (3)': 4626,\
               'bqp50 (4)': 3544,\
               'bqp50 (5)': 4012,\
               'bqp50 (6)': 3693,\
               'bqp50 (7)': 4520,\
               'bqp50 (8)': 4216,\
               'bqp50 (9)': 3780,\
               'bqp50 (10)': 3507,\
               'bqp100 (1)': 7970,\
               'bqp100 (2)': 11036,\
               'bqp100 (3)': 12723,\
               'bqp100 (4)': 10368,\
               'bqp100 (5)': 9083,\
               'bqp100 (6)': 10210,\
               'bqp100 (7)': 10125,\
               'bqp100 (8)': 11435,\
               'bqp100 (9)': 11455,\
               'bqp100 (10)': 12565,\
               'bqp250 (1)': 45607,\
               'bqp250 (2)': 44810,\
               'bqp250 (3)': 49037,\
               'bqp250 (4)': 41274,\
               'bqp250 (5)': 47961,\
               'bqp250 (6)': 41014,\
               'bqp250 (7)': 46757,\
               'bqp250 (8)': 35726,\
               'bqp250 (9)': 48916,\
               'bqp250 (10)': 40442,\
               'bqp500 (1)': 116586,\
               'bqp500 (2)': 128223,\
               'bqp500 (3)': 130812,\
               'bqp500 (4)': 130097,\
               'bqp500 (5)': 125487,\
               'bqp500 (6)': 121719,\
               'bqp500 (7)': 122201,\
               'bqp500 (8)': 123559,\
               'bqp500 (9)': 120798,\
               'bqp500 (10)': 130619,\
               'bqp1000 (1)': 371438,\
               'bqp1000 (2)': 354932,\
               'bqp1000 (3)': 371226,\
               'bqp1000 (4)': 370560,\
               'bqp1000 (5)': 352736,\
               'bqp1000 (6)': 359452,\
               'bqp1000 (7)': 370999,\
               'bqp1000 (8)': 351836,\
               'bqp1000 (9)': 348732,\
               'bqp1000 (10)': 351415,\
               'bqp2500 (1)': 1515011,\
               'bqp2500 (2)': 1468850,\
               'bqp2500 (3)': 1413083,\
               'bqp2500 (4)': 1506943,\
               'bqp2500 (5)': 1491796,\
               'bqp2500 (6)': 1468427,\
               'bqp2500 (7)': 1478654,\
               'bqp2500 (8)': 1484199,\
               'bqp2500 (9)': 1482306,\
               'bqp2500 (10)': 1482354}
        
        if not instance_name in map:
            return None
        else:
            return map[instance_name]


class BQPInstance():
    
    
    def __init__(self, problem, name, num_vars, Q):
        self.problem = problem
        self.name = name
        self.num_vars = num_vars
        self.Q = Q
    
    
    def get_tabu_tenure(self):
        return self.num_vars / 8
    
	
    def get_expected_num_tabu_iterations(self):
        return self.num_vars * 100
    
	
    def get_expected_num_sa_iterations(self):
        return self.num_vars * 1000
    
	
    def generate_random_solution(self):
        vars = zeros((self.num_vars), dtype=int)
        for i in range(self.num_vars):
            vars[i] = (1 if (random.random() > 0.5) else 0)
        
        solution = BQPSolution(self, vars)
        return solution
    
    
    def generate_greedy_randomized_solution(self, k):
        return self.generate_random_solution()
    
    
    def all_moves_generator(self):
        moves = range(self.num_vars)
        random.shuffle(moves)
        while True:
            yield moves
    
    
class BQPSolution():
    
    
    def __init__(self, instance, vars):
        self.instance = instance
        self.vars = vars
    
    
    def __copy__(self):
        return BQPSolution(self.instance, self.vars.copy())
    
    
    def __deepcopy__(self):
        return self.__copy__()
    
    
    def __str__(self):
        vars_str = ''
        for var in self.vars:
            vars_str += str(var) + ','
        return vars_str
    
    
    def draw_solution(self):
        pass
    
    
    def calculate_report_value(self):
        return self.calculate_value()
    
    
    def calculate_value(self):
        return dot(dot(self.vars, self.instance.Q), self.vars)
    
    
    def calculate_move_delta(self, i):
        # Calculate impact of alternating x_i
        delta = dot(self.vars, self.instance.Q[i]) * 2
        
        # Multiply by -1 if the variable is being zeroed
        if self.vars[i] == 1:
            delta = -delta
        
        # Fix double or no counting of the diagonal value by the dot product
        delta += self.instance.Q[i, i]
        
        return delta
    
    
    def generate_random_move(self):
        # Get random index for alternating binary value
        i = random.randint(0, (self.instance.num_vars - 1))
        
        delta = self.calculate_move_delta(i)
        return (i, delta)
    
    
    def apply_move(self, i):
        self.vars[i] = 1 - self.vars[i]
    
    
    def polish(self):
        pass
    
    
    def is_tabu(self, tabu_list, i):
        return (i in tabu_list)
    
    
    def append_tabu(self, tabu_list, i):
        # Add the variable whose value changed to the tabu list
        # to avoid reseting it too early
        tabu_list.append(i)
