LIB_DIR = '../lib'
import sys
from os.path import abspath
sys.path.append(abspath(LIB_DIR))

from tsp import *

import unittest

class tsp_tests(unittest.TestCase):
    
    def setUp(self):
        D_n4 = array([ (0.0, 1, 2, 3),\
                       (  1, 0, 1, 2),\
                       (  2, 1, 0, 1),\
                       (  3, 2, 1, 0) ] )
        self.instance_n4 = (4, D_n4)
        
        D_n5 = array([ (0.0, 1, 2, 3, 4),\
                       (  1, 0, 1, 2, 3),\
                       (  2, 1, 0, 1, 2),\
                       (  3, 2, 1, 0, 1),\
                       (  4, 3, 2, 1, 0) ] )
        self.instance_n5 = (5, D_n5)
    

    def test_apply_move(self):
        solution = ['A', 'B', 'C', 'D', 'E', 'F']
        apply_move(solution, None, (0, 2))
        self.failUnless(solution == ['A', 'C', 'B', 'D', 'E', 'F'])
        
        apply_move(solution, None, (4, 1))
        self.failUnless(solution == ['A', 'C', 'E', 'D', 'B', 'F'])
        
        apply_move(solution, None, (0, 3))
        self.failUnless(solution == ['A', 'D', 'E', 'C', 'B', 'F'])
        
        apply_move(solution, None, (0, 4))
        self.failUnless(solution == ['A', 'B', 'C', 'E', 'D', 'F'])
        
        apply_move(solution, None, (2, 4))
        self.failUnless(solution == ['A', 'B', 'C', 'D', 'E', 'F'])
        

    def test_generate_all_moves(self):
        solution = ['A', 'B', 'C', 'D']
        moves = generate_all_moves(solution, self.instance_n4)
        self.failUnless(moves == [(0, 2), (1, 3)])
        
        solution = ['A', 'B', 'C', 'D', 'E']
        moves = generate_all_moves(solution, self.instance_n5)
        self.failUnless(moves == [(0, 2), (0, 3), (1, 3), (1, 4), (2, 4)])
    

    def test_generate_random_move(self):
        solution = [0, 1, 2, 3]
        possible_moves = [(0, 2), (1, 3)]
        for i in range(1000):
            # Check if only possible moves are generated
            (move, delta) = generate_random_move(solution, self.instance_n4)
            self.failUnless(move in possible_moves)
            
            # Also check if delta is correct
            if move == (0, 2):
                self.failUnless(delta == 2.0)
            elif move == (1, 3):
                self.failUnless(delta == 0.0)

        solution_ = [0, 1, 2, 3, 4]
        possible_moves = [(0, 2), (0, 3), (1, 3), (1, 4), (2, 4)]
        for i in range(1000):
            # Check if only possible moves are generated
            (move, delta) = generate_random_move(solution, self.instance_n5)
            self.failUnless(move in possible_moves)
    
    
    def test_calculate_value(self):
        self.failUnless(calculate_value([0, 1, 2, 3], self.instance_n4) == 6.0)
        self.failUnless(calculate_value([0, 1, 3, 2], self.instance_n4) == 6.0)
        self.failUnless(calculate_value([0, 2, 1, 3], self.instance_n4) == 8.0)
        self.failUnless(calculate_value([0, 2, 3, 1], self.instance_n4) == 6.0)
    
    
    def test_tabu(self):
        tabu_list = []
        
        solution = [0, 1, 2, 3, 4]
        append_tabu(tabu_list, solution, (0, 2))
        self.failUnless(tabu_list == [((0, 1), (3, 2))] or\
                        tabu_list == [((1, 0), (2, 3))] or\
                        tabu_list == [((3, 2), (0, 1))] or\
                        tabu_list == [((2, 3), (1, 0))])
        
        solution = [0, 2, 1, 3, 4]
        self.failUnless(is_tabu(tabu_list, solution, (0, 2)))
        
        solution = [0, 4, 3, 1, 2]
        self.failUnless(is_tabu(tabu_list, solution, (2, 4)))
        
        solution = [2, 0, 4, 3, 1]
        self.failUnless(is_tabu(tabu_list, solution, (0, 3)))
        
        solution = [2, 1, 3, 4, 0]
        self.failUnless(is_tabu(tabu_list, solution, (1, 4)))
    

def main():
    unittest.main()
    
if __name__ == '__main__':
    main()