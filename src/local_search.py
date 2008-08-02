INFINITY = 1e300000
TIME_LIMIT = 60

import psyco
psyco.full()

from os import listdir
from os.path import basename, splitext
from time import time
from numpy import *
import random


class writer:
    def __init__(self, sysout):
        self.sysout = sysout
        self.log = ''

    def write(self, text):
        self.sysout.write(text)
        self.log += text


def estimate_median_delta(instance):
    delta_sample = []
    
    for i in range(40):
        solution = instance.generate_random_solution()
        
        for j in range(10):
            (move, delta) = solution.generate_random_move()
            delta_sample.append(abs(delta))
        
    delta_sample.sort()
    median_delta = delta_sample[len(delta_sample) / 2]
    return median_delta


def grasp(instance, start_time, current_time):
    # Calculate initial solution
    current_solution = instance.generate_greedy_randomized_solution(2)
    current_value = current_solution.calculate_value()
    
    optimization_sense = instance.problem.get_problem_optimization_sense()
    
    value_history = []
    max_value_history = []
    
    best_solution = copy.copy(current_solution)
    max_value = current_value
    
    # Generate all possible moves
    moves = instance.generate_all_moves()

    it = 0
    while (current_time - start_time) < TIME_LIMIT:
        
        # Increment iteration
        it += 1
        
        improving = True
        
        # Start local search
        while improving and (current_time - start_time) < TIME_LIMIT:
            improving = False
            for move in moves:
                delta = current_solution.calculate_move_delta(move)
                
                # If the neighbour solution is better, move to it
                if (delta * optimization_sense) > 0:
                    current_solution.apply_move(move)
                    current_value = current_value + delta
                    improving = True
                    break
            
            current_time = time()
        
        global_improvement = current_value - max_value
        if (global_improvement * optimization_sense) > 0:
            best_solution = copy.copy(current_solution)
            max_value = current_value
        
        # Store historic data
        value_history.append(current_value)
        max_value_history.append(max_value)
        
        # Generate another greedy randomized solution
        current_solution = instance.generate_greedy_randomized_solution(2)
        current_value = current_solution.calculate_value()
        
        current_time = time()
    
    return (best_solution, max_value, value_history, max_value_history, None, None, it)


def tabu_search(instance, start_time, current_time):
    expected_num_iterations = instance.get_expected_num_tabu_iterations()
    
    # Calculate initial solution
    current_solution = instance.generate_random_solution()
    current_value = current_solution.calculate_value()
    
    import copy
    best_solution = copy.copy(current_solution)
    best_value = current_value
    
    optimization_sense = instance.problem.get_problem_optimization_sense()
    
    value_history = []
    best_value_history = []
    
    it = 0
    last_improvement_iteration = 0
    
    # Generate all possible moves
    moves = instance.generate_all_moves()
    random.shuffle(moves)
    
    tabu_list = []
    tabu_tenure = instance.get_tabu_tenure()
    
    # Start local search
    while (current_time - start_time) < TIME_LIMIT:
        
        # Give up if it has been a long time since the last improvement
        if it > expected_num_iterations and \
                (it - last_improvement_iteration) > (expected_num_iterations / 10):
            break
        
        # Store historic data
        value_history.append(current_value)
        best_value_history.append(best_value)
        
        best_move = None
        best_move_delta = -(INFINITY * optimization_sense)
        
        for move in moves:
            delta = current_solution.calculate_move_delta(move)
            
            # If the neighbour solution is better than the current, move to it
            if (delta * optimization_sense) > 0:
                
                # Ignore if this move is tabu
                if current_solution.is_tabu(tabu_list, move):
                    continue
                    
                best_move = move
                best_move_delta = delta
                break
            
            # Otherwise, keep looking for the best neighbour
            elif ((delta - best_move_delta) * optimization_sense) > 0:
                
                # Ignore if this move is tabu
                if current_solution.is_tabu(tabu_list, move):
                    continue
                    
                best_move = move
                best_move_delta = delta
        
        # Append to tabu list and move, if any non-tabu movement was available
        if best_move != None:
            current_solution.append_tabu(tabu_list, best_move)
            current_solution.apply_move(best_move)
            current_value = current_value + best_move_delta
        
        # Remove least recent tabu
        if len(tabu_list) > tabu_tenure:
            tabu_list.pop(0)
        
        # Update best solution found until now, if needed
        global_improvement = current_value - best_value
        if (global_improvement * optimization_sense) > 0:
            last_improvement_iteration = it
            best_solution = copy.copy(current_solution)
            best_value = current_value
        
        # Increment iteration
        it += 1
        
        current_time = time()
        
    return (best_solution, best_value, value_history, best_value_history, None, None, it)


def simulated_annealing(instance, start_time, current_time):
    # Calculate median delta
    median_delta = estimate_median_delta(instance)
    
    expected_num_iterations = instance.get_expected_num_sa_iterations()
	
    # Calculate initial solution
    current_solution = instance.generate_random_solution()
    current_value = current_solution.calculate_value()
    
    import copy
    best_solution = copy.copy(current_solution)
    max_value = current_value

    optimization_sense = instance.problem.get_problem_optimization_sense()
    
    value_history = []
    max_value_history = []
    T_history = []
    P_history = []
    
    it = 0
    last_improvement_iteration = 0
    
    # Start simulated annealing
    while (current_time - start_time) < TIME_LIMIT:
        
        # Give up if it has been a long time since the last improvement
        if it > expected_num_iterations and \
                (it - last_improvement_iteration) > (expected_num_iterations / 10):
            break
        
        # Store historic data
        value_history.append(current_value)
        max_value_history.append(max_value)
        
        # Parameter k defines the steepness of the curve
        k = 10.0
        P_accept_median_delta = exp(-(k * float(it) / float(expected_num_iterations)))
        T_history.append(P_accept_median_delta)
        
        # Generate a neighbour solution
        (move, delta) = current_solution.generate_random_move()
        neighbour_value = current_value + delta
        
        # If the neighbour solution is better, move to it
        if (delta * optimization_sense) >= 0:
            current_solution.apply_move(move)
            current_value = neighbour_value
        else:
            # Otherwise, calculate probability of accepting this suboptimal solution
            P_accept_subopt = median_delta * P_accept_median_delta / (-delta * optimization_sense)
            
            if P_accept_subopt > 1.0: P_accept_subopt = 1.0
            if (delta * optimization_sense) == INFINITY: P_accept_subopt = 0.0
            
            # And move if the suboptimal solution gets lucky
            if random.random() < P_accept_subopt:
                P_history.append((it, P_accept_subopt))
                current_solution.apply_move(move)
                current_value = neighbour_value

        # Update best solution found until now, if needed
        global_improvement = current_value - max_value
        if (global_improvement * optimization_sense) > 0:
            last_improvement_iteration = it
            best_solution = copy.copy(current_solution)
            max_value = current_value
            
        # Increment iteration
        it += 1
        
        current_time = time()
        
    return (best_solution, max_value, value_history, max_value_history, T_history, P_history, it)


def main(algorithm, problem):
    
    random.seed(236887699)
    
    compiled_results = []
    
    instances_dir = problem.get_instances_dir()
    problem_set_files = listdir(instances_dir)
    
    import sys
    saved_sysout = sys.stdout
    sys.stdout = writer(sys.stdout)

    print '> MACHINE SETUP:'
    print 'Processor: Intel Celeron M 410 1.46GHz'
    print 'Memory: 896MB RAM'

    print '> ALGORITHM SETUP:'
    print 'Time limit (seconds):', TIME_LIMIT
    
    for file_name in problem_set_files:
        file_path = instances_dir + file_name
        (problem_set_name, ext) = splitext(basename(file_path))
        
        # Read problem set from the input file
        problem_set = problem.read_problem_set_file(file_path)
        
        optimization_sense = problem.get_problem_optimization_sense()
        
        instance_count = 1
        for instance in problem_set:
            start_time = time()
            current_time = start_time
            
            # Get optimal value
            opt_value = problem.get_opt_value(instance.name)
            
            best_results = None
            best_max_value = - (INFINITY * optimization_sense)
            
            print '--------------------------------------------------------------------'
            print '> INSTANCE:', instance.name
            
            num_restarts = -1
            
            # Run the simulation several times for the instance until the computational time expires
            while (current_time - start_time) < TIME_LIMIT:
                num_restarts += 1
                
                results = algorithm(instance, start_time, current_time)
                (best_solution, max_value, value_history, max_value_history, T_history, P_history, num_iterations) = results
                
                current_time = time()
                
                # Store the best results found until now
                global_improvement = max_value - best_max_value
                if best_results == None or (global_improvement * optimization_sense) > 0:
                    best_results = results
                    best_max_value = max_value
                    print best_max_value
                    
                    # Stopping condition
                    if (opt_value != None):
                        absolute_gap = best_max_value - opt_value
                        if (absolute_gap * optimization_sense) >= 0:
                            break
            
            total_time = current_time - start_time
            
            print '> OVERALL STATISTICS:'
            print 'Total time:', total_time
            print 'Number of restarts:', num_restarts
            
            # Use the best results and the optimal solution for reporting results
            print '> WINNING SIMULATION STATISTICS:'
            (best_solution, max_value, value_history, max_value_history, T_history, P_history, num_iterations) = best_results
            print 'Number of iterations:', num_iterations
            print 'Best solution value:', max_value
            
            percentual_gap = None
            if opt_value != None:
                absolute_gap = opt_value - max_value
                percentual_gap = (absolute_gap * optimization_sense / opt_value) * 100.0
                print 'Optimal value:', opt_value
                print 'Gap:', percentual_gap, '%'
            
            print '> BEST SOLUTION:'
            solution_text = str(best_solution)
            import textwrap
            solution_text = textwrap.fill(solution_text, 100)
            print solution_text
            
            compiled_results.append((instance.name, opt_value, max_value, percentual_gap, total_time))
            
            # Draw graphs about the simulation with best results
            import reports
            reports.report_results(instance.name, best_results, opt_value)
    
    screen_output = sys.stdout.log
    sys.stdout = sys.stdout.sysout

    # Create complete report
    return (compiled_results, screen_output)
    

if __name__ == "__main__":
    from sys import argv
    argv.append('bqp')
    argv.append('sa')
    
    problem = None
    
    if 'bqp' in argv:
        from bqp import *
        problem = BQP()
    elif 'tsp' in argv:
        from tsp import *
        problem = TSP()
    elif 'uctp' in argv:
        from uctp import *
        problem = UCTP()
    elif 'gcp' in argv:
        from gcp import *
        problem = GCP()
    else:
        print "Specify a problem and algorithm, e.g.:"
        print "$ python local_search.py bqp sa"
        exit()

    # Check if any algorithm was specified
    if (not 'gr' in argv) and (not 'ts' in argv) and (not 'sa' in argv):
        print "Specify a problem and algorithm, e.g.:"
        print "$ python local_search.py bqp sa"
        exit()
    
    #import hotshot
    #prof = hotshot.Profile("hotshot_edi_stats")
    
    compiled_results_list = []

    if 'gr' in argv:
        #(compiled_results, screen_output) = prof.runcall(main, grasp, problem)
        (compiled_results, screen_output) = main(grasp, problem)
        compiled_results_list.append(('GR', compiled_results, screen_output))
    if 'ts' in argv:
        #(compiled_results, screen_output) = prof.runcall(main, tabu_search, problem)
        (compiled_results, screen_output) = main(tabu_search, problem)
        compiled_results_list.append(('TS', compiled_results, screen_output))
    if 'sa' in argv:
        #(compiled_results, screen_output) = prof.runcall(main, simulated_annealing, problem)
        (compiled_results, screen_output) = main(simulated_annealing, problem)
        compiled_results_list.append(('SA', compiled_results, screen_output))
    
    #prof.close()
    
    import reports
    reports.report_compiled_results(problem, compiled_results_list)
