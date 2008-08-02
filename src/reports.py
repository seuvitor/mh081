from pylab import *
from datetime import datetime
from os.path import splitext

REPORTS_DIR = '../reports/'


def figure_name(instance_name, algorithm_name):
    name = (instance_name + '_' + algorithm_name)
    name = name.replace('.', '_')
    name = name.replace(' ', '_')
    return name + '.png'

def report_results(instance_name, algorithm_name, results, opt_value):
    (best_solution, max_value, value_history, max_value_history, T_history, P_history, num_iterations) = results
    
    figure(1, figsize=(10,4))
    if T_history != None and P_history != None:
        subplot(211)
    
    title(instance_name)
    plot(range(num_iterations), value_history, linewidth=0.5)
    plot(range(num_iterations), max_value_history, linewidth=0.5)
    if opt_value != None:
        plot(range(num_iterations), [opt_value for i in range(num_iterations)], linewidth=0.5)
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

    figure_path = REPORTS_DIR + figure_name(instance_name, algorithm_name)
    savefig(figure_path, dpi=300, orientation='landscape')
    close()


def report_compiled_results(problem, compiled_results_list):
    (first_algorithm_name, first_compiled_results, first_screen_output) = compiled_results_list[0]
    num_instances = len(first_compiled_results)
    num_algorithms = len(compiled_results_list)
    
    timestamp = datetime.today()
    
    # Set file name and title of report
    report_file_name = problem.get_problem_name()
    report_title = problem.get_problem_name()
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
            '\\usepackage{graphicx}\n'\
            '\\title{Experiment report\\\\\\small{\\textbf{'
    text += report_title
    text += '}}}\n'\
            '\\date{}\n'\
            '\\begin{document}\n'\
            '\\maketitle\n'
    
    # Calculate how many tables will be needed
    DEFAUL_TABLE_LINE_LIMIT = 20
    table_limit = DEFAUL_TABLE_LINE_LIMIT

    num_tables = num_instances / table_limit
    if num_instances % table_limit != 0: num_tables += 1

    text += '\\section{Tables}\n'
    
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
                 
        table += 'instance    &$z*$    '
        table += ('&$z$ &gap    &time ' * num_algorithms)
        table += '\\\\\n'\
                 '\\hline\n'

        # Fill table contents
        begin = i * table_limit
        end = min(num_instances, ((i + 1) * table_limit)) - 1
        
        table_entries = ''
        for j in range(begin, (end + 1)):
            (instance_name, opt_value, tmp_v, tmp_g, tmp_t) = first_compiled_results[j]
            instance_name = instance_name.replace('_','\_')
            if opt_value != None:
                table_entries += '%s & %.0f ' % (instance_name, opt_value)
            else:
                table_entries += '%s & ? ' % (instance_name)
            
            # Fill columns with results from different algorithms
            for (algorithm_name, compiled_results, screen_output) in compiled_results_list:
                
                (tmp_i, tmp_o, best_value, percentual_gap, total_time) = compiled_results[j]
                
                if percentual_gap == 0.0:
                    table_entries += '& \\textbf{%.0f} & %.2f & %.2f ' %\
                        (best_value, percentual_gap, total_time)
                elif percentual_gap != None:
                    table_entries += '& %.0f & %.2f & %.2f ' %\
                        (best_value, percentual_gap, total_time)
                else:
                    table_entries += '& %.0f & ? & %.2f ' %\
                        (best_value, total_time)
                        
            table_entries += '\\\\\n'
            
        # Finish table
        table += table_entries
        table += '\\hline\n'\
                 '\\end{tabular}\n'\
                 '\\end{center}\n'\
                 '\\clearpage\n'
        
        text += table
    
    # Insert graphs for each instance and algorithm
    text += '\\section{Figures}\n'
    for (algorithm_name, compiled_results, screen_output) in compiled_results_list:
        text += '\\subsection{Figures for algorithm ' + algorithm_name + '}\n'
        even = False
        for (instance_name, opt_value, tmp_v, tmp_g, tmp_t) in first_compiled_results:
            text += '\\begin{figure}[hb!]\n'\
                    '\\centering\n'\
                    '\\includegraphics[scale=0.6]{' + figure_name(instance_name, algorithm_name) + '}\n'\
                    '\\caption{' + problem.get_problem_name() + ' ' + algorithm_name + ' ' + instance_name + '}\n'\
                    '\\end{figure}\n'
        
            if even: text += '\\clearpage\n'
            even = not even
        
        if even: text += '\\clearpage\n'
    

    # Insert screen output for each algorithm at the end of the document
    text += '\\section{Execution logs}\n'
    for (algorithm_name, compiled_results, screen_output) in compiled_results_list:
        text += '\\subsection{Detailed output of algorithm ' + algorithm_name + '}\n'
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
