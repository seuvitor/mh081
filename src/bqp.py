def get_problem_optimization_sense():
    MIN = -1
    MAX = 1
    
    return MAX


def get_instances_dir():
    return './bqp_instances/'


def get_problem_name():
    return 'UBQP'


def generate_random_solution(instance_data):
    (num_vars, Q) = instance_data

    from random import random
    random_solution = [(1 if (random() > 0.5) else 0) for i in range(num_vars)]

    return random_solution


def read_instance_data(file):
    line = file.readline()
    [num_vars, num_non_zero] = line.split()
    num_vars, num_non_zero = eval(num_vars), eval(num_non_zero)

    # Create n*n matrix filled with zeroes
    Q = [[0 for i in range(num_vars)] for i in range(num_vars)]
    
    for i in range(num_non_zero):
        line = file.readline()
        [i, j, q_ij] = line.split()
        i, j, q_ij = eval(i), eval(j), eval(q_ij)
        
        # Decrement 1-indexed indices for using in a 0-indexed array
        i -= 1
        j -= 1
        
        Q[i][j] = q_ij
        Q[j][i] = q_ij
        
    instance_data = (num_vars, Q)
    return instance_data
    

def read_problem_set_file(file_path):
    from os.path import basename, splitext
    (problem_set_name, ext) = splitext(basename(file_path))
    
    file = open(file_path, 'r')
    
    line = file.readline()
    num_problems = eval(line.strip())

    instances_list = []
    
    instance_count = 1

    for i in range(num_problems):
        instance_name = problem_set_name + ' (' + str(instance_count) + ')'

        instance_data = read_instance_data(file)

        instance = (instance_name, instance_data)
        instances_list.append(instance)

        instance_count += 1
    
    return instances_list


def get_opt_value(instance_name):
    map = {'bqp50 (1)': 2098.0,\
           'bqp50 (2)': 3702.0,\
           'bqp50 (3)': 4626.0,\
           'bqp50 (4)': 3544.0,\
           'bqp50 (5)': 4012.0,\
           'bqp50 (6)': 3693.0,\
           'bqp50 (7)': 4520.0,\
           'bqp50 (8)': 4216.0,\
           'bqp50 (9)': 3780.0,\
           'bqp50 (10)': 3507.0,\
           'bqp100 (1)': 7970.0,\
           'bqp100 (2)': 11036.0,\
           'bqp100 (3)': 12723.0,\
           'bqp100 (4)': 10368.0,\
           'bqp100 (5)': 9083.0,\
           'bqp100 (6)': 10210.0,\
           'bqp100 (7)': 10125.0,\
           'bqp100 (8)': 11435.0,\
           'bqp100 (9)': 11455.0,\
           'bqp100 (10)': 12565.0,\
           'bqp250 (1)': 45607.0,\
           'bqp250 (2)': 44810.0,\
           'bqp250 (3)': 49037.0,\
           'bqp250 (4)': 41274.0,\
           'bqp250 (5)': 47961.0,\
           'bqp250 (6)': 41014.0,\
           'bqp250 (7)': 46757.0,\
           'bqp250 (8)': 35726.0,\
           'bqp250 (9)': 48916.0,\
           'bqp250 (10)': 40442.0,\
           'bqp500 (1)': 116586.0,\
           'bqp500 (2)': 128223.0,\
           'bqp500 (3)': 130812.0,\
           'bqp500 (4)': 130097.0,\
           'bqp500 (5)': 125487.0,\
           'bqp500 (6)': 121719.0,\
           'bqp500 (7)': 122201.0,\
           'bqp500 (8)': 123559.0,\
           'bqp500 (9)': 120798.0,\
           'bqp500 (10)': 130619.0,\
           'bqp1000 (1)': 371438.0,\
           'bqp1000 (2)': 354932.0,\
           'bqp1000 (3)': 371226.0,\
           'bqp1000 (4)': 370560.0,\
           'bqp1000 (5)': 352736.0,\
           'bqp1000 (6)': 359452.0,\
           'bqp1000 (7)': 370999.0,\
           'bqp1000 (8)': 351836.0,\
           'bqp1000 (9)': 348732.0,\
           'bqp1000 (10)': 351415.0,\
           'bqp2500 (1)': 1515011.0,\
           'bqp2500 (2)': 1468850.0,\
           'bqp2500 (3)': 1413083.0,\
           'bqp2500 (4)': 1506943.0,\
           'bqp2500 (5)': 1491796.0,\
           'bqp2500 (6)': 1468427.0,\
           'bqp2500 (7)': 1478654.0,\
           'bqp2500 (8)': 1484199.0,\
           'bqp2500 (9)': 1482306.0,\
           'bqp2500 (10)': 1482354.0}

    if not instance_name in map:
        return None
    else:
        return map[instance_name]


def calculate_value(solution, instance_data):
    (num_vars, Q) = instance_data
    
    value = 0.0
    
    for i in range(num_vars):
        for j in range(num_vars):
            value += solution[i] * solution[j] * Q[i][j]
    
    return value


def generate_neighbour(solution, instance_data):
    (num_vars, Q) = instance_data
    
    # Get random index for alternating binary value
    from random import randint
    i = randint(0, (num_vars - 1))
    
    x_i = solution[i]

    # Calculate impact of alternating x_i
    sum_i = Q[i][i]
    for j in range(num_vars):
        if j != i:
            sum_i += solution[j] * 2 * Q[i][j]

    # Copy current solution to the neighbour solution
    neighbour = [x for x in solution]
    
    # Alternate value of x_i and set the delta accordingly
    (neighbour[i], delta) = (1, sum_i) if (x_i == 0) else (0, -sum_i)

    return (neighbour, delta)
