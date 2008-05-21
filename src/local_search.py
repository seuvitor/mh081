REPORTS_DIR = '../reports/'
LIB_DIR = '../lib'

INFINITY = 1e300000
DEFAULT_NUM_ITERATIONS = 1000
TIME_LIMIT = 60

import sys
from os.path import abspath
sys.path.append(abspath(LIB_DIR))

import psyco
psyco.full()

from pylab import *
from datetime import datetime
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


def estimate_median_delta(instance_data):
    delta_sample = []
    
    for i in range(40):
        solution = generate_random_solution(instance_data)
	
        for j in range(10):
            (move, delta) = generate_random_move(solution, instance_data)
            delta_sample.append(abs(delta))
        
    delta_sample.sort()
    median_delta = delta_sample[len(delta_sample) / 2]
    return median_delta
    

def report_results(instance_name, results, opt_value):
    (best_solution, max_value, value_history, max_value_history, T_history, P_history, num_iterations) = results
    
    subplot(211)
    title(instance_name)
    plot(range(num_iterations), value_history)
    plot(range(num_iterations), max_value_history)
    if opt_value != None:
        plot(range(num_iterations), [opt_value for i in range(num_iterations)])
    xlabel('iterations')
    ylabel('solution value')

    if T_history != None and P_history != None:
        subplot(212)
        P_history_X = [iteration for (iteration, P) in P_history]
        P_history_Y = [P for (iteration, P) in P_history]
        plot(range(num_iterations), T_history)
        plot(P_history_X, P_history_Y, 'ro', markersize=2)
        [x_min, x_max, y_min, y_max] = axis()
        xlabel('iterations')
        ylabel('T / T_max')

    figure_path = REPORTS_DIR + instance_name + '.png'
    savefig(figure_path)
    close()
    
    
def report_compiled_results(compiled_results_list):
    (first_algorithm_name, first_compiled_results, first_screen_output) = compiled_results_list[0]
    num_instances = len(first_compiled_results)
    num_algorithms = len(compiled_results_list)
    
    timestamp = datetime.today()
    
    # Set file name and title of report
    report_file_name = get_problem_name()
    report_title = get_problem_name()
    for (algorithm_name, compiled_results, screen_output) in compiled_results_list:
        report_file_name += '_' + algorithm_name
        report_title += ' ' + algorithm_name
    report_file_name += '_' + timestamp.strftime('%Y-%m-%d_%Hh%M') + '.tex'
    report_title += ' ' + timestamp.strftime('%d/%m/%Y %Hh%M')

    # Insert latex header
    text = ''
    text += '\\documentclass{article}\n'\
            '\\usepackage{fullpage}\n'\
            '\\usepackage[brazil]{babel}\n'\
            '\\usepackage[latin1]{inputenc}\n'\
            '\\title{Relatorio de experimento\\\\\\small{\\textbf{'
    text += report_title
    text += '}}}\n'\
            '\\date{}\n'\
            '\\begin{document}\n'\
            '\\maketitle\n'\

    # Calculate how many tables will be needed
    DEFAUL_TABLE_LINE_LIMIT = 20
    table_limit = DEFAUL_TABLE_LINE_LIMIT

    num_tables = num_instances / table_limit
    if num_instances % table_limit != 0: num_tables += 1

    # For each table
    for i in range(num_tables):
        #compiled_results_group = compiled_results[i*table_limit:(i+1)*table_limit]

        # Write table header
        table = ''
        table += '\\begin{center}\n'\
                 '\\begin{tabular}{| r r '
        table += ('| r r r ' * num_algorithms)
        table += '|}\n'\
                 '\\hline\n'\
                 '\\multicolumn{2}{| c |}{} '
        
        for (algorithm_name, compiled_results, screen_output) in compiled_results_list:
            table += ' & \\multicolumn{3}{| c |}{' + algorithm_name + '} '
        
        table += '\\\\\n'
                 
        table += 'instance	&$z*$	'
        table += ('&$z$ &gap	&time ' * num_algorithms)
        table += '\\\\\n'\
                 '\\hline\n'

        # Fill table contents
        begin = i * table_limit
        end = min(num_instances, ((i + 1) * table_limit)) - 1
        
        table_entries = ''
        for j in range(begin, (end + 1)):
            (instance_name, opt_value, tmp_v, tmp_g, tmp_t) = first_compiled_results[j]
            instance_name = instance_name.replace('_','\_')
            table_entries += '%s & %.0f ' % (instance_name, opt_value)
            
            # Fill columns with results from different algorithms
            for (algorithm_name, compiled_results, screen_output) in compiled_results_list:
                
                (tmp_i, tmp_o, best_value, percentual_gap, total_time) = compiled_results[j]
                gap = opt_value - best_value
                
                if (gap * get_problem_optimization_sense()) > 0:
                    table_entries += '& %.0f & %.2f & %.2f ' %\
                        (best_value, percentual_gap, total_time)
                else:
                    table_entries += '& \\textbf{%.0f} & %.2f & %.2f ' %\
                        (best_value, percentual_gap, total_time)
                        
            table_entries += '\\\\\n'
            
        # Finish table
        table += table_entries
        table += '\\hline\n'\
                 '\\end{tabular}\n'\
                 '\\end{center}\n'\
                 '\\clearpage\n'
        
        text += table

    # Insert screen output for each algorithm at the end of the document
    for (algorithm_name, compiled_results, screen_output) in compiled_results_list:
        text += '\\center{\\large{\\textbf{Output detalhado do algoritmo ' + algorithm_name + ':}}}\n'
        text += '\\scriptsize\n'
        text += '\\begin{verbatim}\n'
        text += screen_output
        text += '\\end{verbatim}\n'\
                '\\clearpage\n'
        
    text += '\\end{document}'

    # Save report file
    output_file = open(REPORTS_DIR + report_file_name, 'w')
    output_file.write(text)
    output_file.close()
    
    import os
    (filename_without_ext, ext) = splitext(report_file_name)
    os.system('latex.bat ' + filename_without_ext)


def grasp(instance_data, start_time, current_time):
    # Calculate initial solution
    current_solution = generate_greedy_randomized_solution(instance_data, 3)
    current_value = calculate_value(current_solution, instance_data)
    
    optimization_sense = get_problem_optimization_sense()
    
    value_history = []
    max_value_history = []
    
    it = 0
    
    improving = True
    
    # Generate all possible moves
    moves = generate_all_moves(current_solution, instance_data)
    
    # Start local search
    while improving and (current_time - start_time) < TIME_LIMIT:
        
        # Increment iteration
        it += 1
        
        # Store historic data
        value_history.append(current_value)
        max_value_history.append(current_value)
        
        improving = False
        for move in moves:
            delta = calculate_move_delta(current_solution, instance_data, move)
            
            # If the neighbour solution is better, move to it
            if (delta * optimization_sense) > 0:
                apply_move(current_solution, instance_data, move)
                current_value = current_value + delta
                improving = True
                break
        
        current_time = time()
        
    return (current_solution, current_value, value_history, max_value_history, None, None, it)


def tabu_search(instance_data, start_time, current_time):
    expected_num_iterations = get_problem_size(instance_data) * DEFAULT_NUM_ITERATIONS / 10
    
    # Calculate initial solution
    current_solution = generate_random_solution(instance_data)
    current_value = calculate_value(current_solution, instance_data)
    
    best_solution = current_solution
    best_value = current_value
    
    optimization_sense = get_problem_optimization_sense()
    
    value_history = []
    best_value_history = []
    
    it = 0
    last_improvement_iteration = 0
    
    # Generate all possible moves
    moves = generate_all_moves(current_solution, instance_data)
    random.shuffle(moves)
    
    tabu_list = []
    tabu_tenure = get_problem_size(instance_data) / 4
    
    # Start local search
    while (current_time - start_time) < TIME_LIMIT:
        
        # Give up if it has been a long time since the last improvement
        if (it - last_improvement_iteration) > (expected_num_iterations / 10): break
        
        # Store historic data
        value_history.append(current_value)
        best_value_history.append(best_value)
        
        best_move = None
        best_move_delta = -(INFINITY * optimization_sense)
        
        for move in moves:
            delta = calculate_move_delta(current_solution, instance_data, move)
            
            # If the neighbour solution is better than the current, move to it
            if (delta * optimization_sense) > 0:
                
                # Ignore if this move is tabu
                if is_tabu(tabu_list, current_solution, move):
                    continue
                    
                best_move = move
                best_move_delta = delta
                break
            
            # Otherwise, keep looking for the best neighbour
            elif ((delta - best_move_delta) * optimization_sense) > 0:
                
                # Ignore if this move is tabu
                if is_tabu(tabu_list, current_solution, move):
                    continue
                    
                best_move = move
                best_move_delta = delta
        
        # Append to tabu list and move, if any non-tabu movement was available
        if best_move != None:
            append_tabu(tabu_list, current_solution, best_move)
            apply_move(current_solution, instance_data, best_move)
            current_value = current_value + best_move_delta
        
        # Remove least recent tabu
        if len(tabu_list) > tabu_tenure:
            tabu_list.pop(0)
        
        # Update best solution found until now, if needed
        global_improvement = current_value - best_value
        if (global_improvement * optimization_sense) > 0:
            last_improvement_iteration = it
            best_solution = current_solution
            best_value = current_value
        
        # Increment iteration
        it += 1
        
        current_time = time()
        
    return (best_solution, best_value, value_history, best_value_history, None, None, it)


def simulated_annealing(instance_data, start_time, current_time):
    # Calculate median delta
    median_delta = estimate_median_delta(instance_data)
    
    expected_num_iterations = get_problem_size(instance_data) * DEFAULT_NUM_ITERATIONS

    # Calculate initial solution
    current_solution = generate_random_solution(instance_data)
    current_value = calculate_value(current_solution, instance_data)
    
    best_solution = current_solution
    max_value = current_value

    optimization_sense = get_problem_optimization_sense()
    
    value_history = []
    max_value_history = []
    T_history = []
    P_history = []
    
    it = 0
    last_improvement_iteration = 0
    
    # Start simulated annealing
    while (current_time - start_time) < TIME_LIMIT:
        
        # Give up if it has been a long time since the last improvement
        if (it - last_improvement_iteration) > (expected_num_iterations / 10): break
        
        # Store historic data
        value_history.append(current_value)
        max_value_history.append(max_value)
        
        # Parameter k defines the steepness of the curve
        k = 10.0
        P_accept_median_delta = exp(-(k * float(it) / float(expected_num_iterations)))
        T_history.append(P_accept_median_delta)
        
        # Generate a neighbour solution
        (move, delta) = generate_random_move(current_solution, instance_data)
        neighbour_value = current_value + delta
        
        # If the neighbour solution is better, move to it
        if (delta * optimization_sense) >= 0:
            apply_move(current_solution, instance_data, move)
            current_value = neighbour_value
        else:
            # Otherwise, calculate probability of accepting this suboptimal solution
            P_accept_subopt = median_delta * P_accept_median_delta / (-delta * optimization_sense)
            
            if P_accept_subopt > 1.0: P_accept_subopt = 1.0
            if (delta * optimization_sense) == INFINITY: P_accept_subopt = 0.0
            
            # And move if the suboptimal solution gets lucky
            if random.random() < P_accept_subopt:
                P_history.append((it, P_accept_subopt))
                apply_move(current_solution, instance_data, move)
                current_value = neighbour_value

        # Update best solution found until now, if needed
        global_improvement = current_value - max_value
        if (global_improvement * optimization_sense) > 0:
            last_improvement_iteration = it
            best_solution = current_solution
            max_value = current_value
            
        # Increment iteration
        it += 1
        
        current_time = time()
        
    return (best_solution, max_value, value_history, max_value_history, T_history, P_history, it)


def main(algorithm):
    
    random.seed(236887699)
    
    compiled_results = []
    
    instances_dir = get_instances_dir()
    problem_set_files = listdir(instances_dir)
    
    import sys
    saved_sysout = sys.stdout
    sys.stdout = writer(sys.stdout)

    print '> MACHINE SETUP:'
    print 'Processor: Intel Celeron M 410 1.46GHz'
    print 'Memory: 896MB RAM'

    print '> ALGORITHM SETUP:'
    print 'Number of iterations (per instance size unit):', str(DEFAULT_NUM_ITERATIONS)
    print 'Time limit (seconds):', TIME_LIMIT
    
    for file_name in problem_set_files:
        file_path = instances_dir + file_name
        (problem_set_name, ext) = splitext(basename(file_path))
        
        # Read problem set from the input file
        problem_set = read_problem_set_file(file_path)
        
        optimization_sense = get_problem_optimization_sense()
        
        instance_count = 1
        for instance in problem_set:
            (instance_name, instance_data) = instance
            
            start_time = time()
            current_time = start_time
            
            # Get optimal value
            opt_value = get_opt_value(instance_name)
            
            best_results = None
            best_max_value = - (INFINITY * optimization_sense)
            
            print '--------------------------------------------------------------------'
            print '> INSTANCE:', instance_name
            
            num_restarts = -1
            
            # Run the simulation several times for the instance until the computational time expires
            while (current_time - start_time) < TIME_LIMIT:
                num_restarts += 1
                
                results = algorithm(instance_data, start_time, current_time)
                (best_solution, max_value, value_history, max_value_history, T_history, P_history, num_iterations) = results
                
                current_time = time()
                
                # Store the best results found until now
                global_improvement = max_value - best_max_value
                if best_results == None or (global_improvement * optimization_sense) > 0:
                    best_results = results
                    best_max_value = max_value
                    print best_max_value
                    
                    # Stopping condition
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
            
            if opt_value != None:
                absolute_gap = opt_value - max_value
                percentual_gap = (absolute_gap * optimization_sense / opt_value) * 100.0
                print 'Optimal value:', opt_value
                print 'Gap:', percentual_gap, '%'
            
            print '> BEST SOLUTION:'
            solution_text = ''
            for i in range(len(best_solution)):
                solution_text += str(best_solution[i]) + ','
            import textwrap
            solution_text = textwrap.fill(solution_text, 100)
            print solution_text
            
            compiled_results.append((instance_name, opt_value, max_value, percentual_gap, total_time))
            
            # Draw graphs about the simulation with best results
            report_results(instance_name, best_results, opt_value)
    
    screen_output = sys.stdout.log
    sys.stdout = sys.stdout.sysout

    # Create complete report
    return (compiled_results, screen_output)
    

if __name__ == "__main__":
    from sys import argv
    argv.append('bqp')
    argv.append('sa')

    if 'bqp' in argv:
        from bqp import *
    elif 'tsp' in argv:
        from tsp import *
    elif 'uctp' in argv:
        from uctp import *
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
        #(compiled_results, screen_output) = prof.runcall(main, grasp)
        (compiled_results, screen_output) = main(grasp)
        compiled_results_list.append(('GR', compiled_results, screen_output))
    if 'ts' in argv:
        #(compiled_results, screen_output) = prof.runcall(main, tabu_search)
        (compiled_results, screen_output) = main(tabu_search)
        compiled_results_list.append(('TS', compiled_results, screen_output))
    if 'sa' in argv:
        #(compiled_results, screen_output) = prof.runcall(main, simulated_annealing)
        (compiled_results, screen_output) = main(simulated_annealing)
        compiled_results_list.append(('SA', compiled_results, screen_output))
    
    #prof.close()
    
    report_compiled_results(compiled_results_list)
