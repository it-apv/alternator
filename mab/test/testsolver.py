'''
Created on Oct 12, 2012

@author: jonathan
'''
import unittest
import mab.constraints

def read_settings(settings_file='SETTINGS'):
    settings = {}
    f = open(settings_file)

    for line in f:
        if not line.startswith('#'):
            split_line = line.strip().split(' ', 1)
            settings[split_line[0]] = split_line[1]

    f.close()
    return settings

class TestSolver(unittest.TestCase):


    def setUp(self):
        self.settings = read_settings()
        self.solver = mab.constraints.Solver(self.settings['solver'])
        self.assertFalse(self.solver.proc==None)


    def tearDown(self):
        pass

    def test_is_wellformed_statement(self):
        self.assertTrue(mab.constraints.is_wellformed_statement("()()"))
        self.assertTrue(mab.constraints.is_wellformed_statement("(())()"))
        self.assertFalse(mab.constraints.is_wellformed_statement("()(()"))

    def test_set_query(self):
        q = '(declare-fun x () Int)'
        self.solver.add_statement(q)
        q2 = '(declare-fun y () Int)(declare-fun z () Int)'
        self.solver.add_statement(q2)
        

    def test_is_satisfiable(self):
        q = '(declare-fun x () Int)(declare-fun y () Int)(declare-fun z () Int)' + \
            '(assert (>= (* 2 x) (+ y z))) (assert (= x 1))'
        self.solver.add_statement(q)
        self.assertTrue(self.solver.is_satisfiable())
        

    def test_get_var_val(self):
        q = '(declare-fun x () Int)(declare-fun y () Int)(assert (> x 1))' + \
            '(assert (< x 3))(assert (= x y))'
        self.solver.add_statement(q)
        self.assertTrue(self.solver.is_satisfiable())
        self.assertTrue(self.solver.get_var_val('x') == 2)
        self.assertTrue(self.solver.get_var_val('y') == 2)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testConstraints']
    unittest.main()