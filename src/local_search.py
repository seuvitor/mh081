INFINITY = 1e300000
TIME_LIMIT = 60
DETAILED_SA_HISTORY = True

import psyco
psyco.full()

from os import listdir
from os.path import basename, splitext
from time import time
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
    
    print '>> Starting GRASP...'
    
    # Calculate initial solution
    current_solution = instance.generate_greedy_randomized_solution(2)
    current_value = current_solution.calculate_value()
    
    optimization_sense = instance.problem.get_problem_optimization_sense()
    
    value_history = []
    best_value_history = []
    
    best_solution = copy.copy(current_solution)
    best_value = current_value
    
    # Generate all possible moves
    all_moves = instance.all_moves_generator().next

    it = 0
    while (current_time - start_time) < TIME_LIMIT:
        
        # Increment iteration
        it += 1
        
        improving = True
        
        # Start local search
        while improving and (current_time - start_time) < TIME_LIMIT:
            improving = False
            for move in all_moves():
                delta = current_solution.calculate_move_delta(move)
                
                # If the neighbour solution is better, move to it
                if (delta * optimization_sense) > 0:
                    current_solution.apply_move(move)
                    current_value = current_value + delta
                    improving = True
                    break
            
            current_time = time()
        
        global_improvement = current_value - best_value
        if (global_improvement * optimization_sense) > 0:
            best_solution = copy.copy(current_solution)
            best_value = current_value
            print 'Best solution objective value in', str(current_time - start_time) + 's:', best_value
        
        # Store historic data
        value_history.append(current_value)
        best_value_history.append(best_value)
        
        # Generate another greedy randomized solution
        current_solution = instance.generate_greedy_randomized_solution(2)
        current_value = current_solution.calculate_value()
        
        current_time = time()
    
    print 'End of GRASP.'
    print 'final solution objective value:', best_solution.calculate_value()
    best_solution.polish()
    print 'polished solution objective value:', best_solution.calculate_value()
    
    report_value = best_solution.calculate_report_value()
    return (best_solution, report_value, value_history, best_value_history, None, None, it)


def tabu_search(instance, start_time, current_time):
    expected_num_iterations = instance.get_expected_num_tabu_iterations()
    
    # Calculate initial solution
    current_solution = instance.generate_random_solution()
    current_value = current_solution.calculate_value()
    
    import copy
    best_solution = copy.copy(current_solution)
    best_value = current_value
    distance_from_best_value = 0
    
    optimization_sense = instance.problem.get_problem_optimization_sense()
    
    value_history = []
    best_value_history = []
    
    it = 0
    last_improvement_iteration = 0
    
    # Generate all possible moves
    all_moves = instance.all_moves_generator().next
    
    tabu_list = []
    tabu_tenure = instance.get_tabu_tenure()
    
    print '>> Starting tabu search...'
    print 'expected_num_iterations', expected_num_iterations
    print 'initial solution objective value:', best_value
    
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
        
        for move in all_moves():
            delta = current_solution.calculate_move_delta(move)
            
            # If the neighbour solution is better than the current, move to it
            if (delta * optimization_sense) > 0:
                
                # Ignore if this move is tabu and the neighbor solution
                # doesn't represent a global improvement
                if current_solution.is_tabu(tabu_list, move) and \
                        abs(delta) <= distance_from_best_value:
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
            print 'best_value', best_value, 'report_value', best_solution.calculate_report_value()
            distance_from_best_value = 0
        else:
            distance_from_best_value = abs(global_improvement)
        
        # Increment iteration
        it += 1
        
        current_time = time()
    
    print 'End of tabu search.'
    print 'final solution objective value:', best_solution.calculate_value()
    best_solution.polish()
    print 'polished solution objective value:', best_solution.calculate_value()
    
    report_value = best_solution.calculate_report_value()
    return (best_solution, report_value, value_history, best_value_history, None, None, it)


def simulated_annealing(instance, start_time, current_time):
    # Calculate median delta
    median_delta = estimate_median_delta(instance)
    
    expected_num_iterations = instance.get_expected_num_sa_iterations()
	
    # Calculate initial solution
    current_solution = instance.generate_random_solution()
    current_value = current_solution.calculate_value()
    
    import copy
    best_solution = copy.copy(current_solution)
    best_value = current_value

    optimization_sense = instance.problem.get_problem_optimization_sense()
    
    value_history = []
    best_value_history = []
    
    T_history = None
    P_history = None
    if DETAILED_SA_HISTORY:
        T_history = []
        P_history = []
    
    it = 0
    last_improvement_iteration = 0
    
    print '>> Starting simulated annealing...'
    print 'expected_num_iterations', expected_num_iterations
    print 'initial solution objective value:', best_value
    
    # Start simulated annealing
    while (current_time - start_time) < TIME_LIMIT:
        
        # Give up if it has been a long time since the last improvement
        if it > expected_num_iterations and \
                (it - last_improvement_iteration) > (expected_num_iterations / 10):
            break
        
        # Store historic data
        value_history.append(current_value)
        best_value_history.append(best_value)
        
        # Parameter k defines the steepness of the curve
        k = 10.0
        P_accept_median_delta = exp(-(k * float(it) / float(expected_num_iterations)))
        
        if DETAILED_SA_HISTORY:
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
                current_solution.apply_move(move)
                current_value = neighbour_value
                if DETAILED_SA_HISTORY:
                    P_history.append((it, P_accept_subopt))

        # Update best solution found until now, if needed
        global_improvement = current_value - best_value
        if (global_improvement * optimization_sense) > 0:
            last_improvement_iteration = it
            best_solution = copy.copy(current_solution)
            best_value = current_value
            print 'best_value', best_value, 'report_value', best_solution.calculate_report_value()
            
        # Increment iteration
        it += 1
        
        current_time = time()
    
    print 'End of simulated annealing.'
    print 'final solution objective value:', best_solution.calculate_value()
    best_solution.polish()
    print 'polished solution objective value:', best_solution.calculate_value()
    
    report_value = best_solution.calculate_report_value()
    return (best_solution, report_value, value_history, best_value_history, T_history, P_history, it)


def main(algorithm, algorithm_name, problem):
    
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
    
    for file_name in sorted(problem_set_files):
        file_path = instances_dir + file_name
        (problem_set_name, ext) = splitext(basename(file_path))
        
        # Read problem set from the input file
        problem_set = problem.read_problem_set_file(file_path)
        
        optimization_sense = problem.get_problem_optimization_sense()
        
        instance_count = 1
        for instance in problem_set:
            random.seed(236887699)
            
            start_time = time()
            current_time = start_time
            
            # Get optimal value
            opt_value = problem.get_opt_value(instance.name)
            
            best_results = None
            global_best_value = - (INFINITY * optimization_sense)
            
            print '--------------------------------------------------------------------'
            print '> INSTANCE:', instance.name
            
            num_restarts = -1
            
            # Run the simulation several times for the instance until the computational time expires
            while (current_time - start_time) < TIME_LIMIT:
                num_restarts += 1
                
                results = algorithm(instance, start_time, current_time)
                (best_solution, best_value, value_history, best_value_history, T_history, P_history, num_iterations) = results
                
                current_time = time()
                
                # Store the best results found until now
                global_improvement = best_value - global_best_value
                if best_results == None or (global_improvement * optimization_sense) > 0:
                    best_results = results
                    global_best_value = best_value
                    print 'Best solution in', str(current_time - start_time) + 's:', global_best_value
                    
                    # Stopping condition
                    if (opt_value != None):
                        absolute_gap = global_best_value - opt_value
                        if (absolute_gap * optimization_sense) >= 0:
                            break
            
            total_time = current_time - start_time
            
            print '> OVERALL STATISTICS:'
            print 'Total time:', total_time
            print 'Number of restarts:', num_restarts
            
            # Use the best results and the optimal solution for reporting results
            print '> WINNING SIMULATION STATISTICS:'
            (best_solution, best_value, value_history, best_value_history, T_history, P_history, num_iterations) = best_results
            print 'Number of iterations:', num_iterations
            print 'Best solution value:', best_value
            
            percentual_gap = None
            if opt_value != None:
                absolute_gap = opt_value - best_value
                percentual_gap = (float(absolute_gap * optimization_sense) / opt_value) * 100.0
                print 'Optimal value:', opt_value
                print 'Gap:', percentual_gap, '%'
            
            print '> BEST SOLUTION:'
            solution_text = str(best_solution)
            import textwrap
            solution_text = textwrap.fill(solution_text, 100)
            print solution_text
            
            compiled_results.append((instance.name, opt_value, best_value, percentual_gap, total_time))
            
            # Draw graphs about the simulation with best results
            import reports
            reports.report_results(instance.name, algorithm_name, best_results, opt_value)
    
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
    elif 'cvrp' in argv:
        from cvrp import *
        problem = CVRP()
    elif 'dsp' in argv:
        from dsp import *
        problem = DSP()
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
        #(compiled_results, screen_output) = prof.runcall(main, grasp, 'GR', problem)
        (compiled_results, screen_output) = main(grasp, 'GR', problem)
        compiled_results_list.append(('GR', compiled_results, screen_output))
    if 'ts' in argv:
        #(compiled_results, screen_output) = prof.runcall(main, tabu_search, 'TS', problem)
        (compiled_results, screen_output) = main(tabu_search, 'TS', problem)
        compiled_results_list.append(('TS', compiled_results, screen_output))
    if 'sa' in argv:
        #(compiled_results, screen_output) = prof.runcall(main, simulated_annealing, 'SA', problem)
        (compiled_results, screen_output) = main(simulated_annealing, 'SA', problem)
        compiled_results_list.append(('SA', compiled_results, screen_output))
    
    #prof.close()
    
    import reports
    reports.report_compiled_results(problem, compiled_results_list)
