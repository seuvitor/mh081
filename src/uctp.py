from numpy import *
import random
from os.path import basename, splitext
import copy
from bisect import bisect_left

NUM_TIMESLOTS = 45
 

def get_problem_optimization_sense():
    MIN = -1
    MAX = 1
    
    return MIN


def get_instances_dir():
    return '../uctp_instances/'


def get_problem_name():
    return 'UCTP'


def get_problem_size(instance_data):
    (num_events, num_rooms, num_features, num_students,\
            room_sizes, attendance, room_features, event_features,\
            suitable_rooms, common_attendance) = instance_data
    return num_events


def generate_random_solution(instance_data):
    (num_events, num_rooms, num_features, num_students,\
            room_sizes, attendance, room_features, event_features,\
            suitable_rooms, common_attendance) = instance_data
    
    events_assignments = zeros(num_events, dtype=int)
    timeslots_occupation = [list() for timeslot in range(NUM_TIMESLOTS)]
    
    # Allocate events to timeslots
    for event in range(num_events):
        timeslot = event % NUM_TIMESLOTS
        events_assignments[event] = timeslot
        timeslots_occupation[timeslot].append(event)
    
    # Calculate initial penalties of timeslots
    timeslots_penalties = zeros(NUM_TIMESLOTS, dtype=int)
    for timeslot in range(NUM_TIMESLOTS):
        timeslots_penalties[timeslot] = calculate_timeslot_penalty(\
                timeslots_occupation[timeslot], instance_data)
    
    return (events_assignments, timeslots_occupation, timeslots_penalties)


def generate_greedy_randomized_solution(instance_data, k):
    return generate_random_solution(instance_data)


def draw_solution(instance_data, solution):
    return
    
    
def read_instance_data(file):
    
    # Read number of events, rooms, features and students
    num_events, num_rooms, num_features, num_students = file.readline().split()
    
    # Convert strings to integers
    num_events = int(num_events)
    num_rooms = int(num_rooms)
    num_features = int(num_features)
    num_students = int(num_students)    
    
    # Read room sizes
    room_sizes = zeros(num_rooms, dtype=int)
    for i in range(num_rooms):
        room_sizes[i] = eval(file.readline())
    
    # Read events attendance
    attendance = zeros((num_events, num_students), dtype=int)
    for i in range(num_students):
        for j in range(num_events):
            attendance[j, i] = eval(file.readline())

    # Read features available in rooms
    room_features = zeros((num_rooms, num_features), dtype=int)
    for i in range(num_rooms):
        for j in range(num_features):
            room_features[i, j] = eval(file.readline())

    # Read features required by events
    event_features = zeros((num_events, num_features), dtype=int)
    for i in range(num_events):
        for j in range(num_features):
            event_features[i, j] = eval(file.readline())

    # Create list of suitable rooms for every event
    suitable_rooms = [list() for i in range(num_events)]
    for event in range(num_events):
        for room in range(num_rooms):
            room_suits_event = True
            for feature in range(num_features):
                if event_features[event, feature] == 1 and room_features[room, feature] != 1:
                    room_suits_event = False
                    break
            if room_suits_event:
                suitable_rooms[event].append(room)
    
    # Calculate common attendace (in number of students) of pairs of events
    common_attendance = zeros((num_events, num_events), dtype=int)
    for e1 in range(num_events):
        for e2 in range(num_events):
            if e1 < e2:
                common_attendance[e1, e2] = dot(attendance[e1], attendance[e2])
    
    instance_data = (num_events, num_rooms, num_features, num_students,\
                     room_sizes, attendance, room_features, event_features,\
                     suitable_rooms, common_attendance)
    
    return instance_data


def read_problem_set_file(file_path):
    (problem_set_name, ext) = splitext(basename(file_path))
    
    file = open(file_path, 'r')
    
    instance_name = problem_set_name
    instance_data = read_instance_data(file)
    
    instance = (instance_name, instance_data)
    
    return [instance]


def get_opt_value(instance_name):
    return 1.0


# Hopcroft-Karp bipartite max-cardinality matching and max independent set
# David Eppstein, UC Irvine, 27 Apr 2002

def bipartite_match(graph):
    '''Find maximum cardinality matching of a bipartite graph (U,V,E).
    The input format is a dictionary mapping members of U to a list
    of their neighbors in V.  The output is a triple (M,A,B) where M is a
    dictionary mapping members of V to their matches in U, A is the part
    of the maximum independent set in U, and B is the part of the MIS in V.
    The same object may occur in both U and V, and is treated as two
    distinct vertices if this happens.'''
    
    # initialize greedy matching (redundant, but faster than full search)
    matching = {}
    for u in graph:
        for v in graph[u]:
            if v not in matching:
                matching[v] = u
                break
    
    while 1:
        # structure residual graph into layers
        # pred[u] gives the neighbor in the previous layer for u in U
        # preds[v] gives a list of neighbors in the previous layer for v in V
        # unmatched gives a list of unmatched vertices in final layer of V,
        # and is also used as a flag value for pred[u] when u is in the first layer
        preds = {}
        unmatched = []
        pred = dict([(u,unmatched) for u in graph])
        for v in matching:
            del pred[matching[v]]
        layer = list(pred)
        
        # repeatedly extend layering structure by another pair of layers
        while layer and not unmatched:
            newLayer = {}
            for u in layer:
                for v in graph[u]:
                    if v not in preds:
                        newLayer.setdefault(v,[]).append(u)
            layer = []
            for v in newLayer:
                preds[v] = newLayer[v]
                if v in matching:
                    layer.append(matching[v])
                    pred[matching[v]] = v
                else:
                    unmatched.append(v)
        
        # did we finish layering without finding any alternating paths?
        if not unmatched:
            unlayered = {}
            for u in graph:
                for v in graph[u]:
                    if v not in preds:
                        unlayered[v] = None
            return (matching,list(pred),list(unlayered))
    
        # recursively search backward through layers to find alternating paths
        # recursion returns true if found path, false otherwise
        def recurse(v):
            if v in preds:
                L = preds[v]
                del preds[v]
                for u in L:
                    if u in pred:
                        pu = pred[u]
                        del pred[u]
                        if pu is unmatched or recurse(pu):
                            matching[v] = u
                            return 1
            return 0
    
        for v in unmatched: recurse(v)


def greedy_bipartite_match(graph):
    matching = {}
    for u in graph:
        for v in graph[u]:
            if v not in matching:
                matching[v] = u
                break
    return matching


def calculate_timeslot_penalty(timeslot_events, instance_data):
    (num_events, num_rooms, num_features, num_students,\
            room_sizes, attendance, room_features, event_features,\
            suitable_rooms, common_attendance) = instance_data
    
    penalty = 0
    
    # For each pair of events in the timeslot
    for i in range(len(timeslot_events)):
        for j in range(len(timeslot_events)):
            if i < j:
                (e1, e2) = (timeslot_events[i], timeslot_events[j])
                # Penalize for every student that attends to both events
                penalty += common_attendance[e1, e2]
    
    # For each event, add edges to rooms that suits its needs
    E = {}
    for event in timeslot_events:
        E[event] = suitable_rooms[event]
    
    # Find matching between events and rooms
    (matching, temp1, temp2) = bipartite_match(E)
    #matching = greedy_bipartite_match(E)
    
    # Allocate events appearing in the matching
    events_in_room = list()
    for room in range(num_rooms):
        events_in_room.append(list())
        if matching.has_key(room):
            events_in_room[room].append(matching[room])
    
    # Allocate events that didn't appear on the matching
    allocated_events = set()
    allocated_events.update(matching.values())
    for event in timeslot_events:
        if event not in allocated_events:
            
            # Put event in the suitable room with the least number of events in
            suitable_rooms = E[event]
            best_room = suitable_rooms[0]
            for room in suitable_rooms:
                if len(events_in_room[room]) < len(events_in_room[best_room]):
                    best_room = room
            
            events_in_room[best_room].append(event)
            allocated_events.add(event)
            
    # Penalize events scheduled to the same timeslot and room
    for room_events in events_in_room:
        if len(room_events) > 1:
            penalty += (len(room_events) - 1)
            
    return penalty


def calculate_value(solution, instance_data):
    (num_events, num_rooms, num_features, num_students,\
            room_sizes, attendance, room_features, event_features,\
            suitable_rooms, common_attendance) = instance_data
    
    (events_assignments, timeslots_occupation, timeslots_penalties) = solution

    # The solution value is the sum of the penalties for each timeslot
    return sum(timeslots_penalties)


def calculate_move_delta(solution, instance_data, (moving_event, jump)):
    (num_events, num_rooms, num_features, num_students,\
            room_sizes, attendance, room_features, event_features,\
            suitable_rooms, common_attendance) = instance_data
    
    (events_assignments, timeslots_occupation, timeslots_penalties) = solution
    
    old_timeslot = events_assignments[moving_event]
    new_timeslot = (old_timeslot + jump) % NUM_TIMESLOTS
    
    delta = 0
    
    delta -= timeslots_penalties[old_timeslot]
    delta -= timeslots_penalties[new_timeslot]

    changed_old_timeslot = list(timeslots_occupation[old_timeslot])
    changed_old_timeslot.remove(moving_event)
    
    changed_new_timeslot = list(timeslots_occupation[new_timeslot])
    insertion_index = bisect_left(timeslots_occupation[new_timeslot], moving_event)
    changed_new_timeslot.insert(insertion_index, moving_event)
    
    delta += calculate_timeslot_penalty(changed_old_timeslot, instance_data)
    delta += calculate_timeslot_penalty(changed_new_timeslot, instance_data)
    
    return delta


def generate_all_moves(solution, instance_data):
    (events_assignments, timeslots_occupation, timeslots_penalties) = solution
    
    num_events = len(events_assignments)
    
    moves = []
    
    for moving_event in range(num_events):
        for jump in range(1, NUM_TIMESLOTS - 1):
            moves.append((moving_event, jump))

    return moves


def generate_random_move(solution, instance_data):
    (events_assignments, timeslots_occupation, timeslots_penalties) = solution
    
    num_events = len(events_assignments)
    
    moving_event = random.randint(0, (num_events - 1))
    jump = random.randint(1, (NUM_TIMESLOTS - 2))
    delta = calculate_move_delta(solution, instance_data, (moving_event, jump))
    return ((moving_event, jump), delta)
    
    
def apply_move(solution, instance_data, (moving_event, jump)):
    (events_assignments, timeslots_occupation, timeslots_penalties) = solution
    
    old_timeslot = events_assignments[moving_event]
    new_timeslot = (old_timeslot + jump) % NUM_TIMESLOTS
    
    # Assign the event to the new timeslot
    events_assignments[moving_event] = new_timeslot
    
    # Update timeslots occupation
    timeslots_occupation[old_timeslot].remove(moving_event)

    insertion_index = bisect_left(timeslots_occupation[new_timeslot], moving_event)
    timeslots_occupation[new_timeslot].insert(insertion_index, moving_event)
    
    # Recalculate penalties for changed timeslots
    timeslots_penalties[old_timeslot] = calculate_timeslot_penalty(\
            timeslots_occupation[old_timeslot], instance_data)
    timeslots_penalties[new_timeslot] = calculate_timeslot_penalty(\
            timeslots_occupation[new_timeslot], instance_data)


def is_tabu(tabu_list, solution, (i, j)):
    size = len(solution)
    a, b = solution[i], solution[(i + 1) % size]
    d, c = solution[j], solution[(j + 1) % size]
    
    # This movement is tabu if it is trying to construct an edge that was
    # recently removed, i.e. that is still in the tabu list
    for tabu in tabu_list:
        (e1, e2) = tabu
        if e1 == (a, d) or e1 == (d, a) or e2 == (a, d) or e2 == (d, a)\
                or e1 == (b, c) or e1 == (c, b) or e2 == (b, c) or e2 == (c, b):
            return True
    return False


def append_tabu(tabu_list, solution, (i, j)):
    size = len(solution)
    
    a, b = solution[i], solution[(i + 1) % size]
    d, c = solution[j], solution[(j + 1) % size]
    
    # Append removed edges to the tabu list to avoid their early reconstruction
    tabu_list.append(((a, b), (c, d)))
