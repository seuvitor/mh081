def get_problem_optimization_sense():
    MIN = -1
    MAX = 1
    
    return MIN


def get_instances_dir():
    return './tsp_instances/'


def generate_random_solution(instance_data):
    (vertices, edges, distances) = instance_data
    
    from random import shuffle
    random_solution = [id_v for (id_v, x_v, y_v) in vertices]
    shuffle(random_solution)

    return random_solution


def read_instance_data(file):
    vertices = []
    edges = {}
    distances = {}
    
    # Get cities coordinates from the input file
    line = file.readline()
    while not line.startswith('EOF'):
        [id, x, y] = line.split()
        vertices.append((id, eval(x), eval(y)))
        line = file.readline()

    # Initialize adjacency lists
    for (id_v, x_v, y_v) in vertices:
        edges[id_v] = []

    # Create edges between cities
    from math import sqrt
    for (id_u, x_u, y_u) in vertices:
        for (id_v, x_v, y_v) in vertices:
            if id_u == id_v: continue
            d_uv = sqrt(((x_v - x_u)**2) + ((y_v - y_u)**2))
            edges[id_u].append((id_v, d_uv))
            edges[id_v].append((id_u, d_uv))
            distances[(id_u, id_v)] = d_uv
            distances[(id_v, id_u)] = d_uv

    instance_data = (vertices, edges, distances)
    return instance_data
    

def read_problem_set_file(file_path):
    from os.path import basename, splitext
    (problem_set_name, ext) = splitext(basename(file_path))
    
    file = open(file_path, 'r')
    
    for i in range(6): file.readline() # Skip header lines

    instance_name = problem_set_name
    instance_data = read_instance_data(file)
    
    instance = (instance_name, instance_data)
    
    return [instance]


def get_opt_value(instance_name):
    map = {'berlin52': 7542.0,\
           'bier127': 118282.0,\
           'ch130': 6110.0}

    if not instance_name in map:
        return None
    else:
        return map[instance_name]


def calculate_value(solution, instance_data):
    (vertices, edges, distances) = instance_data
    tour = solution
    
    value = 0.0
    
    # Add weights of edges linking consecutive vertices in the tour
    for i in range(len(tour) - 1):
        id_u, id_v = tour[i], tour[i + 1]
        value = value + distances[(id_u, id_v)]
    
    # Add the weight of the returning edge
    id_start, id_end = tour[0], tour[len(tour) - 1]
    value = value + distances[(id_end, id_start)]
    
    return value


def generate_neighbour(solution, instance_data):
    (vertices, edges, distances) = instance_data
    tour = solution
    
    size = len(tour)
    
    # Get random indexes for swapping
    from random import randint
    i = randint(0, (size - 1))
    j = (i + randint(1, size - 2)) % size
    
    neighbour = [v_id for v_id in tour]

    # Get ids of the former predecessor and successor of the moving element
    id_old_pred = neighbour[(i - 1) % size]
    id_old_succ = neighbour[(i + 1) % size]
    
    # Remove the moving element from its old position
    id_v = neighbour.pop(i)
    
    # In this special case, the former first element must move to the end
    if j == 0:
        first = neighbour.pop(0)
        neighbour.append(first)

    # Insert the moving element in its new position
    neighbour.insert(j, id_v)
    
    # Get ids of the new predecessor and successor of the moving element
    id_new_pred = neighbour[(j - 1) % size]
    id_new_succ = neighbour[(j + 1) % size]

    # Calculate the value variation in changing the tour
    delta = distances[(id_new_pred, id_v)] + distances[(id_v, id_new_succ)] - distances[(id_new_pred, id_new_succ)]\
            - distances[(id_old_pred, id_v)] - distances[(id_v, id_old_succ)] + distances[(id_old_pred, id_old_succ)]

    return (neighbour, delta)
