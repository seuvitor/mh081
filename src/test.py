LIB_DIR = '../lib'
import sys
from os.path import abspath
sys.path.append(abspath(LIB_DIR))

from tsp import *

def test_tabu():
    tabu_list = []
    
    print 'test tabu'
    solution = ['A', 'B', 'C', 'D', 'E']
    print generate_all_moves(solution, None)
    t = append_tabu(tabu_list, solution, (2,1))
    print tabu_list[0] == ('B', 'D')
    
    print 'test is_tabu'
    solution = ['A', 'C', 'B', 'D', 'E']
    
    print not is_tabu(tabu_list, solution, (0,1))
    print is_tabu(tabu_list, solution, (0,2))
    print not is_tabu(tabu_list, solution, (0,3))
    print is_tabu(tabu_list, solution, (1,2))
    print not is_tabu(tabu_list, solution, (1,3))
    print not is_tabu(tabu_list, solution, (1,4))
    
    print is_tabu(tabu_list, solution, (2,3))
    print is_tabu(tabu_list, solution, (2,4))
    print is_tabu(tabu_list, solution, (2,1))
    print is_tabu(tabu_list, solution, (3,4))
    print is_tabu(tabu_list, solution, (3,1))
    print is_tabu(tabu_list, solution, (3,2))
    
    print not is_tabu(tabu_list, solution, (4,1))
    print not is_tabu(tabu_list, solution, (4,2))
    print is_tabu(tabu_list, solution, (4,3))

test_tabu()