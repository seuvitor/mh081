from numpy import *
import random
from os.path import basename, splitext
import copy
import bisect

INFINITY = 1e300000
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

    causing_hcv = zeros(num_events, dtype=int)

    # Calculate initial penalties of timeslots
    timeslots_penalties = zeros(NUM_TIMESLOTS, dtype=int)
    for timeslot in range(NUM_TIMESLOTS):
        timeslots_penalties[timeslot] = calculate_timeslot_penalty(\
                timeslots_occupation[timeslot], instance_data, causing_hcv)

    return (events_assignments, timeslots_occupation, timeslots_penalties, causing_hcv)


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


def calculate_timeslot_penalty(timeslot_events, instance_data, causing_hcv = None):
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
                if causing_hcv != None and common_attendance[e1, e2] > 0:
                    causing_hcv[e1] = 1
                    causing_hcv[e2] = 1
    
    # For each event, add edges to rooms that suits its needs
    E = {}
    for event in timeslot_events:
        E[event] = suitable_rooms[event]
    
    # Find matching between events and rooms
    (matching, temp1, temp2) = bipartite_match(E)
    
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
    
    (events_assignments, timeslots_occupation, timeslots_penalties, causing_hcv) = solution

    # The solution value is the sum of the penalties for each timeslot
    return sum(timeslots_penalties)


def calculate_move_delta(solution, instance_data, (move_type, move_data)):
    (num_events, num_rooms, num_features, num_students,\
            room_sizes, attendance, room_features, event_features,\
            suitable_rooms, common_attendance) = instance_data
    
    (events_assignments, timeslots_occupation, timeslots_penalties, causing_hcv) = solution
    
    delta = 0
    
    if move_type == 'INS':
        (moving_event, jump) = move_data
        old_timeslot = events_assignments[moving_event]
        new_timeslot = (old_timeslot + jump) % NUM_TIMESLOTS
        
        # Return infity so that this move is forbiden
        if len(timeslots_occupation[new_timeslot]) >= num_rooms or\
                causing_hcv[moving_event] == 0:
            return INFINITY
        
        delta -= timeslots_penalties[old_timeslot]
        delta -= timeslots_penalties[new_timeslot]
        
        changed_old_timeslot = list(timeslots_occupation[old_timeslot])
        changed_old_timeslot.remove(moving_event)
        
        changed_new_timeslot = list(timeslots_occupation[new_timeslot])
        bisect.insort_left(changed_new_timeslot, moving_event)
        
        delta += calculate_timeslot_penalty(changed_old_timeslot, instance_data)
        delta += calculate_timeslot_penalty(changed_new_timeslot, instance_data)
    
    elif move_type == 'SWAP':
        (event_1, event_2) = move_data
        timeslot_1 = events_assignments[event_1]
        timeslot_2 = events_assignments[event_2]
    
        # Return infity so that this move is forbiden
        if timeslot_1 == timeslot_2 or\
                causing_hcv[event_1] == 0:# or causing_hcv[event_2] == 0:
            return INFINITY
    
        delta -= timeslots_penalties[timeslot_1]
        delta -= timeslots_penalties[timeslot_2]
        
        changed_timeslot_1 = list(timeslots_occupation[timeslot_1])
        changed_timeslot_1.remove(event_1)
        bisect.insort_left(changed_timeslot_1, event_2)
        
        changed_timeslot_2 = list(timeslots_occupation[timeslot_2])
        changed_timeslot_2.remove(event_2)
        bisect.insort_left(changed_timeslot_2, event_1)
        
        delta += calculate_timeslot_penalty(changed_timeslot_1, instance_data)
        delta += calculate_timeslot_penalty(changed_timeslot_2, instance_data)
    
    return delta


def generate_all_moves(solution, instance_data):
    (events_assignments, timeslots_occupation, timeslots_penalties, causing_hcv) = solution
    
    num_events = len(events_assignments)
    
    moves = []

    # Generate all moves of type INS
    ins_moves = []
    for moving_event in range(num_events):
        for jump in range(1, NUM_TIMESLOTS - 1):
            ins_moves.append(('INS', (moving_event, jump)))
    random.shuffle(ins_moves)
    moves.extend(ins_moves)
    
    # Generate all moves of type SWAP
    swap_moves = []
    for e1 in range(num_events):
        for e2 in range(num_events):
            if e1 < e2:
                swap_moves.append(('SWAP', (e1, e2)))
    random.shuffle(swap_moves)
    moves.extend(swap_moves)
    
    return moves


def generate_random_move(solution, instance_data):
    (events_assignments, timeslots_occupation, timeslots_penalties, causing_hcv) = solution
    
    num_events = len(events_assignments)
    
    move = None
    
    # Generate move of type INS with probability 0.8
    if random.random() < 0.8:
        moving_event = random.randint(0, (num_events - 1))
        jump = random.randint(1, (NUM_TIMESLOTS - 2))
        move = ('INS', (moving_event, jump))
    
    # Otherwise, genereate move of type SWAP
    else:
        event_1 = random.randint(0, (num_events - 1))
        event_2 = (event_1 + random.randint(1, (num_events - 1))) % num_events
        if event_1 < event_2:
            move = ('SWAP', (event_1, event_2))
        else:
            if event_1 == event_2:
            move = ('SWAP', (event_2, event_1))
    
    delta = calculate_move_delta(solution, instance_data, move)
    return (move, delta)
    
    
def apply_move(solution, instance_data, (move_type, move_data)):
    (events_assignments, timeslots_occupation, timeslots_penalties, causing_hcv) = solution
    
    if move_type == 'INS':
        (moving_event, jump) = move_data
        
        old_timeslot = events_assignments[moving_event]
        new_timeslot = (old_timeslot + jump) % NUM_TIMESLOTS
        
        # Assign the event to the new timeslot
        events_assignments[moving_event] = new_timeslot
        
        # Update timeslots occupation
        timeslots_occupation[old_timeslot].remove(moving_event)
        bisect.insort_left(timeslots_occupation[new_timeslot], moving_event)
        
        # Reset hcv flag for events in timeslots affected by the move
        for event in timeslots_occupation[old_timeslot] + timeslots_occupation[new_timeslot]:
            causing_hcv[event] = 0
        
        # Recalculate penalties for changed timeslots
        timeslots_penalties[old_timeslot] = calculate_timeslot_penalty(\
                timeslots_occupation[old_timeslot], instance_data, causing_hcv)
        timeslots_penalties[new_timeslot] = calculate_timeslot_penalty(\
                timeslots_occupation[new_timeslot], instance_data, causing_hcv)
    
    elif move_type == 'SWAP':
        (event_1, event_2) = move_data
        
        timeslot_1 = events_assignments[event_1]
        timeslot_2 = events_assignments[event_2]
        
        # Assign the event to the new timeslot
        events_assignments[event_1] = timeslot_2
        events_assignments[event_2] = timeslot_1
        
        # Update timeslots occupation
        timeslots_occupation[timeslot_1].remove(event_1)
        bisect.insort_left(timeslots_occupation[timeslot_2], event_1)
        timeslots_occupation[timeslot_2].remove(event_2)
        bisect.insort_left(timeslots_occupation[timeslot_1], event_2)
        
        # Reset hcv flag for events in timeslots affected by the move
        for event in timeslots_occupation[timeslot_1] + timeslots_occupation[timeslot_2]:
            causing_hcv[event] = 0
        
        # Recalculate penalties for changed timeslots
        timeslots_penalties[timeslot_1] = calculate_timeslot_penalty(\
                timeslots_occupation[timeslot_1], instance_data, causing_hcv)
        timeslots_penalties[timeslot_2] = calculate_timeslot_penalty(\
                timeslots_occupation[timeslot_2], instance_data, causing_hcv)


def is_tabu(tabu_list, solution, (move_type, move_data)):
    (events_assignments, timeslots_occupation, timeslots_penalties, causing_hcv) = solution
    
    if move_type == 'INS':
        (moving_event, jump) = move_data
        
        new_timeslot = (events_assignments[moving_event] + jump) % NUM_TIMESLOTS
        
        # This movement is tabu if it is trying to assign the event to a timeslot
        # from which it was recently removed, i.e. that is still in the tabu list
        return (('INS', moving_event, new_timeslot) in tabu_list)
    
    elif move_type == 'SWAP':
        (event_1, event_2) = move_data
        
        if event_1 <= event_2:
            return ('SWAP', event_1, event_2) in tabu_list
        else:
            return ('SWAP', event_2, event_1) in tabu_list


def append_tabu(tabu_list, solution, (move_type, move_data)):
    (events_assignments, timeslots_occupation, timeslots_penalties, causing_hcv) = solution
    
    if move_type == 'INS':
        (moving_event, jump) = move_data
        
        old_timeslot = events_assignments[moving_event]
        
        # Append assignment of event to the old timeslot to the tabu list
        tabu_list.append(('INS', moving_event, old_timeslot))
    
    elif move_type == 'SWAP':
        (event_1, event_2) = move_data
        
        if event_1 <= event_2:
            tabu_list.append(('SWAP', event_1, event_2))
        else:
            tabu_list.append(('SWAP', event_2, event_1))
