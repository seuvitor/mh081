REPORTS_DIR = './reports/'
LIB_DIR = './lib'

INFINITY = 1e300000
DEFAULT_NUM_ITERATIONS = 10000
DEFAULT_NUM_SIMULATIONS = 100

import sys
from os.path import abspath
sys.path.append(abspath(LIB_DIR))

from pylab import *
from datetime import datetime
from os import listdir
from os.path import basename, splitext
from time import time
from numpy import *
import random

def estimate_median_delta(instance_data):
    delta_sample = []
    
    for i in range(40):
        solution = generate_random_solution(instance_data)

        for j in range(10):
            (neighbour, delta) = generate_neighbour(solution, instance_data)
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
    
    
def report_compiled_results(compiled_results):
    timestamp = datetime.today()
    
    report_file_name = get_problem_name() + '_' + timestamp.strftime('%Y-%m-%d_%Hh%M') + '.tex'
    report_title = get_problem_name() + ' ' + timestamp.strftime('%d/%m/%Y, %Hh%M')

    text = ''
    text += '\\documentclass{article}\n'\
            '\\usepackage[brazil]{babel}\n'\
            '\\usepackage[latin1]{inputenc}\n'\
            '\\title{Relatorio de experimento\\\\\\small{'
    text += report_title
    text += '}}\n'\
            '\\date{}\n'\
            '\\begin{document}\n'\
            '\\maketitle\n'\

    DEFAUL_TABLE_LINE_LIMIT = 20
    table_limit = DEFAUL_TABLE_LINE_LIMIT
    
    num_tables = len(compiled_results) / table_limit
    if len(compiled_results) % table_limit != 0: num_tables += 1
    
    for i in range(num_tables):
        compiled_results_group = compiled_results[i*table_limit:(i+1)*table_limit]

        table = ''
        table += '\\begin{center}\n'\
                 '\\begin{tabular}{r r r r r}\n'\
                 '\\hline\n'\
                 'instance	&$z*$	&$z$	&gap (\\%)	&time (s) \\\\\n'\
                 '\\hline\n'

        table_entries = ''
        for (instance_name, opt_value, best_value, percentual_gap, total_time) in compiled_results_group:
                    
            if best_value < opt_value:
                table_entries += '%s & %.0f & %.0f & %.2f & %.2f \\\\\n' %\
                    (instance_name, opt_value, best_value, percentual_gap, total_time)
            else:
                table_entries += '%s & %.0f & \\textbf{%.0f} & %.2f & %.2f \\\\\n' %\
                    (instance_name, opt_value, best_value, percentual_gap, total_time)
                    
        table += table_entries
        table += '\\hline\n'\
                 '\\end{tabular}\n'\
                 '\\end{center}\n'\
                 '\\clearpage\n'
        
        text += table
    
    text += '\\end{document}'

    output_file = open('./reports/' + report_file_name, 'w')
    output_file.write(text)
    output_file.close()


def local_search(instance_data, params):
    (median_delta) = params
    max_num_iterations = DEFAULT_NUM_ITERATIONS

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
    while it < max_num_iterations:
        
        # Give up if it has been a long time since the last improvement
        if (it - last_improvement_iteration) > (max_num_iterations / 10): break

        # Store historic data
        value_history.append(current_value)
        max_value_history.append(max_value)
        
        # Parameter k defines the steepness of the curve
        k = 10.0
        P_accept_median_delta = exp(-(k * float(it) / float(max_num_iterations)))
        T_history.append(P_accept_median_delta)
        
        # Generate a neighbour solution
        (neighbour, delta) = generate_neighbour(current_solution, instance_data)
        neighbour_value = current_value + delta
        
        # If the neighbour solution is better, move to it
        if (delta * optimization_sense) >= 0:
            current_solution = neighbour
            current_value = neighbour_value
        else:
            # Otherwise, calculate probability of accepting this suboptimal solution
            P_accept_subopt = median_delta * P_accept_median_delta / (-delta * optimization_sense)
            
            if P_accept_subopt > 1.0: P_accept_subopt = 1.0
            
            # And move if the suboptimal solution gets lucky
            if random.random() < P_accept_subopt:
                P_history.append((it, P_accept_subopt))
                current_solution = neighbour
                current_value = neighbour_value

        # Update best solution found until now, if needed
        global_improvement = current_value - max_value
        if (global_improvement * optimization_sense) > 0:
            last_improvement_iteration = it
            best_solution = current_solution
            max_value = current_value
            
        # Increment iteration
        it += 1
        
    return (best_solution, max_value, value_history, max_value_history, T_history, P_history, it)


def main():
    
    random.seed(236887699)
    
    compiled_results = []
    
    instances_dir = get_instances_dir()
    problem_set_files = listdir(instances_dir)

    for file_name in ['bqp50.txt', 'bqp100.txt']:#problem_set_files:
        file_path = instances_dir + file_name
        (problem_set_name, ext) = splitext(basename(file_path))

        # Read problem set from the input file
        problem_set = read_problem_set_file(file_path)
        
        optimization_sense = get_problem_optimization_sense()
        
        instance_count = 1
        for instance in problem_set:
            (instance_name, instance_data) = instance
            
            start_time = time()
            
            # Calculate good simulation params
            median_delta = estimate_median_delta(instance_data)
            params = (median_delta)
            
            # Get optimal value
            opt_value = get_opt_value(instance_name)
            
            best_results = None
            best_max_value = - (INFINITY * optimization_sense)
            
            print '--------------------------------------------------------------------'
            print '> instance:', instance_name
            
            num_simulations = DEFAULT_NUM_SIMULATIONS
            
            # Run the simulation several times for the instance
            for i in range(num_simulations):
                results = local_search(instance_data, params)
                (best_solution, max_value, value_history, max_value_history, T_history, P_history, num_iterations) = results
                
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
            
            end_time = time()
            total_time = end_time - start_time
            
            # Use the best results and the optimal solution for reporting results
            (best_solution, max_value, value_history, max_value_history, T_history, P_history, num_iterations) = best_results
            print '> num_iterations:', num_iterations
            print '> best_solution:', best_solution
            print '> max_value:', max_value
            
            if opt_value != None:
                absolute_gap = opt_value - max_value
                percentual_gap = (absolute_gap * optimization_sense / opt_value) * 100.0
                print '> opt_value:', opt_value
                print '> gap:', percentual_gap, '%'

            compiled_results.append((instance_name, opt_value, max_value, percentual_gap, total_time))
            
            # Draw graphs about the simulation with best results
            report_results(instance_name, best_results, opt_value)
    
    # Create table with overall results
    report_compiled_results(compiled_results)

if __name__ == "__main__":
    from sys import argv
    argv.append('bqp')

    if 'bqp' in argv:
        from bqp import *
    elif 'tsp' in argv:
        from tsp import *
    else:
        print "Specify a problem, e.g.:"
        print "$ python local_search.py bqp"
        exit()

    #import hotshot
    #prof = hotshot.Profile("hotshot_edi_stats")
    #prof.runcall(main)
    #prof.close()
    main()
