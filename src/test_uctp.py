LIB_DIR = '../lib'
import sys
from os.path import abspath
sys.path.append(abspath(LIB_DIR))

import unittest
from uctp import *


class uctp_tests(unittest.TestCase):
    
    
    def setUp(self):
        problem_set = read_problem_set_file('../uctp_instances/small_1.tim')
        (instance_name, instance_data) = problem_set[0]
        self.instance_data = instance_data
    
    
    def test_calculate_value(self):
        solution = generate_random_solution(self.instance_data)
        value_before_move = calculate_value(solution, self.instance_data)
        
        NUM_TIMESLOTS = 45
        
        for i in range(1, (NUM_TIMESLOTS - 1)):
            move = (0, i)
            delta_move = calculate_move_delta(solution, self.instance_data, move)
            
            apply_move(solution, self.instance_data, move)
            value_after_move = calculate_value(solution, self.instance_data)
            self.failUnless(value_before_move + delta_move == value_after_move)
            
            move = (0, (NUM_TIMESLOTS - i))
            delta_move_back = calculate_move_delta(solution, self.instance_data, move)
            self.failUnless(delta_move + delta_move_back == 0)
            
            apply_move(solution, self.instance_data, move)
            value_after_move_back = calculate_value(solution, self.instance_data)
            self.failUnless(value_after_move + delta_move_back == value_after_move_back)
            
            self.failUnless(value_before_move == value_after_move_back)
        


def main():
    unittest.main()
    
if __name__ == '__main__':
    main()