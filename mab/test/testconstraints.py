'''
Created on Oct 12, 2012

@author: jonathan
'''
import unittest
import mab.constraints
import mab.test.testautomata
import mab.test.testsolver

class ConstraintTest(unittest.TestCase):


    def setUp(self):
        self.a = mab.test.testautomata.get_small_automaton()
        self.a.export('a')
        self.a2 = mab.test.testautomata.get_small_automaton_2()
        self.a2.export('a2')
        self.a3 = mab.test.testautomata.get_small_automaton_3()
        self.a3.export('a3')
        self.al = mab.test.testautomata.get_larger_automaton()
        self.al.export('al')
        self.al2 = mab.test.testautomata.get_larger_automaton_2()
        self.al2.export('al2')
        self.a_tricky = mab.test.testautomata.get_tricky_automaton()
        self.a_tricky.export('a_tricky')
        
    
    def tearDown(self):
        pass


    def testConstraintGenerator(self):
        mab.constraints.ConstraintGenerator({'foo': self.a}, 'multiset')

        
    def test_generate_multiset(self):
        cg = mab.constraints.ConstraintGenerator({'foo': self.a}, 'multiset')
        small_q = cg.generate({'bound': 2, 'bad': 's1', 'role': 'foo'})
        self.assertEqual(small_q.count('declare-fun'),
                         get_number_of_vars(self.a, 'multiset', 2))
        for var in ['f_foo_s0_S_2_eps_eps_foo_s0_R_2', 'f_foo_s1_R_2_eps_eps_foo_s0_R_2']:
            self.assertTrue(small_q.find(var) > -1)
        self.assertEqual(small_q.count('assert'),
                         get_number_of_asserts(self.a, 'multiset', 2))
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        self.assertFalse(s1.is_satisfiable())
        

    def test_generate_l_multiset(self):
        bound = 3
        cg = mab.constraints.ConstraintGenerator({'foo': self.al}, 'multiset')
        small_q = cg.generate({'bound': bound, 'bad': 's1', 'role': 'foo'})
        self.assertEqual(small_q.count('declare-fun'),
                         get_number_of_vars(self.al, 'multiset', bound))
        self.assertEqual(small_q.count('assert'),
                         get_number_of_asserts(self.al, 'multiset', bound))
        for var in ['f_foo_s0_S_2_eps_eps_foo_s0_R_2', 'f_foo_s0_S_1_send_foo_foo_tmp_S_1']:
            self.assertTrue(small_q.find(var) > -1)
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        self.assertTrue(s1.is_satisfiable())
        

    def test_generate_l_lossy(self):
        bound = 1
        cg = mab.constraints.ConstraintGenerator({'foo': self.al}, 'lossy')
        small_q = cg.generate({'bound': bound, 'bad': 's1', 'role': 'foo'})
        cg.bounded_automata['foo'].export()
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        # This automaton receives in the reverse order of sending. Thus it should not work with
        # lossy channel semantics.
        ans = s1.is_satisfiable()
        if ans:
            for k, v in s1.model.iteritems():
                print k + ': ' + str(v)
        self.assertFalse(ans)


    def test_generate_l2(self):
        bound = 1
        cg = mab.constraints.ConstraintGenerator({'foo': self.al2}, 'multiset')
        small_q = cg.generate({'bound': bound, 'bad': 's1', 'role': 'foo'})
        self.assertEqual(small_q.count('declare-fun'),
                         get_number_of_vars(self.al, 'multiset', bound))
        self.assertEqual(small_q.count('assert'),
                         get_number_of_asserts(self.al, 'multiset', bound))
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        self.assertFalse(s1.is_satisfiable())
        

    def test_generate_l3(self):
        bound = 2
        cg = mab.constraints.ConstraintGenerator({'foo': self.al2}, 'multiset')
        small_q = cg.generate({'bound': bound, 'bad': 's1', 'role': 'foo'})
        self.assertEqual(small_q.count('declare-fun'),
                         get_number_of_vars(self.al, 'multiset', bound))
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        self.assertTrue(s1.is_satisfiable())
        

    def test_generate_l2_lossy(self):
        bound = 2
        cg = mab.constraints.ConstraintGenerator({'foo': self.al2}, 'lossy')
        small_q = cg.generate({'bound': bound, 'bad': 's1', 'role': 'foo'})
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        # Possible, requires a bound of 2
        ans = s1.is_satisfiable()
        self.assertTrue(ans)
        

    def test_generate_l3_lossy(self):
        bound = 2
        cg = mab.constraints.ConstraintGenerator({'foo': self.al2}, 'lossy')
        small_q = cg.generate({'bound': bound, 'bad': 's1', 'role': 'foo'})
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        # Possible because requires a bound of 2
        query_file = open('tmp/l3_lossy.query', 'w')
        query_file.write(small_q)
        self.assertTrue(s1.is_satisfiable())
        

    def test_generate_2(self):
        bound = 1
        cg = mab.constraints.ConstraintGenerator({'foo': self.a2}, 'multiset')
        small_q = cg.generate({'bound': bound, 'bad': 's1', 'role': 'foo'})
        self.assertEqual(small_q.count('declare-fun'), 
                         get_number_of_vars(self.a2, 'multiset', bound))
        for var in ['f_foo_s0_S_1_eps_eps_foo_s0_R_1', 'f_foo_s1_R_1_eps_eps_foo_s0_R_1']:
            self.assertTrue(small_q.find(var) > -1)
        self.assertEqual(small_q.count('assert'), 
                         get_number_of_asserts(self.a2, 'multiset', bound))
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        self.assertTrue(s1.is_satisfiable())
        
    def test_generate_3_multiset(self):
        cg = mab.constraints.ConstraintGenerator({'foo': self.a3}, 'multiset')
        small_q = cg.generate({'bound': 2, 'bad': 's1', 'role': 'foo'})
        self.assertEqual(small_q.count('declare-fun'), 
                         get_number_of_vars(self.a3, 'multiset', 2))
        for var in ['f_foo_s0_S_2_eps_eps_foo_s0_R_2', 'f_foo_s1_R_2_eps_eps_foo_s0_R_2']:
            self.assertTrue(small_q.find(var) > -1)
        self.assertEqual(small_q.count('assert'), 
                         get_number_of_asserts(self.a3, 'multiset', 2))
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        self.assertFalse(s1.is_satisfiable())
        
    def test_generate_3_lossy(self):
        cg = mab.constraints.ConstraintGenerator({'foo': self.a3}, 'lossy')
        small_q = cg.generate({'bound': 1, 'bad': 's1', 'role': 'foo'})
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        self.assertFalse(s1.is_satisfiable())
        
    def test_generate_for_tricky(self):
        cg = mab.constraints.ConstraintGenerator({'tricky': self.a_tricky}, 'multiset')
        small_q = cg.generate({'bound': 2, 'bad': 'b', 'role': 'tricky'})
        self.assertEqual(small_q.count('declare-fun'),
                         get_number_of_vars(self.a_tricky, 'multiset', 2))
        self.assertEqual(small_q.count('assert'), 
                         get_number_of_asserts(self.a_tricky, 'multiset', 2))
        settings = mab.test.testsolver.read_settings()
        s1 = mab.constraints.Solver(settings['solver'])
        s1.add_statement(small_q)
        
        self.assertFalse(s1.is_satisfiable())
        
        
    def test_that_all_states_are_accepting(self):
        sender = mab.test.testautomata.get_msg_sender('sender', 'foo')
        receiver = mab.test.testautomata.get_msg_receiver('receiver', 'bar')
        settings = mab.test.testsolver.read_settings()
        automata_dict = {}
        automata_dict['sender'] = sender
        automata_dict['receiver'] = receiver
        
        settings['role'] = 'sender'
        settings['bad'] = '1'
        settings['bound'] = 2
        settings['semantics'] = 'multiset'
        
        cs = mab.constraints.ConstraintSolver(automata_dict, settings)
        self.assertTrue(cs.has_solution(), 'Should be accepted!')

        
    def test_that_all_states_are_accepting_2(self):
        sender = mab.test.testautomata.get_msg_sender('sender', 'foo')
        receiver = mab.test.testautomata.get_msg_receiver('receiver', 'bar')
        settings = mab.test.testsolver.read_settings()
        automata_dict = {}
        automata_dict['sender'] = sender
        automata_dict['receiver'] = receiver
        
        settings['role'] = 'receiver'
        settings['bad'] = '2'
        settings['bound'] = 2
        settings['semantics'] = 'multiset'
        
        cs = mab.constraints.ConstraintSolver(automata_dict, settings)
        self.assertFalse(cs.has_solution(), 'Should not be accepted!')


    def test_multiple_automata_2_lossy_simplest(self):
        sender = mab.test.testautomata.get_msg_sender('sender', 'foo')
        receiver = mab.test.testautomata.get_msg_receiver('receiver', 'foo')
        settings = mab.test.testsolver.read_settings()
        automata_dict = {}
        automata_dict['sender'] = sender
        automata_dict['receiver'] = receiver
        
        settings['role'] = 'receiver'
        settings['bad'] = '2'
        settings['bound'] = 2
        settings['semantics'] = 'lossy'
        
        cs = mab.constraints.ConstraintSolver(automata_dict, settings)
        self.assertTrue(cs.has_solution(), 'Should be accepted!')


    def test_multiple_automata(self):
        sender = mab.test.testautomata.get_linear_msg_sender('sender', 'foo', 4)
        receiver = mab.test.testautomata.get_linear_msg_receiver('receiver', 'foo', 4)
        settings = mab.test.testsolver.read_settings()
        automata_dict = {}
        automata_dict['sender'] = sender
        automata_dict['receiver'] = receiver
        
        settings['role'] = 'receiver'
        settings['bad'] = '3'
        settings['bound'] = 3
        settings['semantics'] = 'multiset'
        
        cs = mab.constraints.ConstraintSolver(automata_dict, settings)
        self.assertTrue(cs.has_solution(), 'Should be accepted!')


    def test_multiple_automata_2(self):
        sender = mab.test.testautomata.get_linear_msg_sender('sender', 'foo', 4)
        receiver = mab.test.testautomata.get_linear_msg_receiver('receiver', 'foo', 5)
        settings = mab.test.testsolver.read_settings()
        automata_dict = {}
        automata_dict['sender'] = sender
        automata_dict['receiver'] = receiver
        
        settings['role'] = 'receiver'
        settings['bad'] = '4'
        settings['bound'] = 2
        settings['semantics'] = 'multiset'
        
        cs = mab.constraints.ConstraintSolver(automata_dict, settings)
        self.assertFalse(cs.has_solution(), 'Should not be accepted!')
        
        
    def test_multiple_automata_2_lossy(self):
        sender = mab.test.testautomata.get_linear_msg_sender('sender', 'foo', 4)
        receiver = mab.test.testautomata.get_linear_msg_receiver('receiver', 'foo', 5)
        settings = mab.test.testsolver.read_settings()
        automata_dict = {}
        automata_dict['sender'] = sender
        automata_dict['receiver'] = receiver
        
        settings['role'] = 'receiver'
        settings['bad'] = '4'
        settings['bound'] = 2
        settings['semantics'] = 'lossy'
        
        cs = mab.constraints.ConstraintSolver(automata_dict, settings)
        self.assertFalse(cs.has_solution(), 'Should not be accepted!')
        
        
    def test_multiple_automata_2_lossy_2(self):
        sender = mab.test.testautomata.get_linear_msg_sender('sender', 'foo', 4)
        receiver = mab.test.testautomata.get_linear_msg_receiver('receiver', 'foo', 5)
        settings = mab.test.testsolver.read_settings()
        automata_dict = {}
        automata_dict['sender'] = sender
        automata_dict['receiver'] = receiver
        
        settings['role'] = 'receiver'
        settings['bad'] = '4'
        settings['bound'] = 2
        settings['semantics'] = 'lossy'
        
        cs = mab.constraints.ConstraintSolver(automata_dict, settings)
        self.assertFalse(cs.has_solution(), 'Should not be accepted!')
        
        
    def test_multiple_automata_2_lossy_5(self):
        for i in range(1,13,3):
            for j in range(1,13,3):
                
                sender = mab.test.testautomata.get_linear_msg_sender('sender', 'foo', i)
                receiver = mab.test.testautomata.get_linear_msg_receiver('receiver', 'foo', j)
                settings = mab.test.testsolver.read_settings()
                automata_dict = {}
                automata_dict['sender'] = sender
                automata_dict['receiver'] = receiver
                
                settings['role'] = 'receiver'
                settings['bad'] = str(j-1)
                settings['bound'] = 2
                settings['semantics'] = 'lossy'
                
                cs = mab.constraints.ConstraintSolver(automata_dict, settings)
                if i < j:
                    self.assertFalse(cs.has_solution(),
                                     'Should not be accepted, i=' + str(i) + ' j=' + str(j))
                else:
                    ans = cs.has_solution()
                    if not ans:
                        print cs.get_query()
                    self.assertTrue(ans, 'Should be accepted, i=' + str(i) + ' j=' + str(j))
                    
        
    def test_multiple_automata_2_stuttering(self):
        sender = mab.test.testautomata.get_linear_msg_sender('sender', 'foo', 1)
        receiver = mab.test.testautomata.get_linear_msg_receiver('receiver', 'foo', 2)
        settings = mab.test.testsolver.read_settings()
        automata_dict = {}
        automata_dict['sender'] = sender
        automata_dict['receiver'] = receiver
        
        settings['role'] = 'receiver'
        settings['bad'] = '1'
        settings['bound'] = 2
        settings['semantics'] = 'stuttering'
        
        cs = mab.constraints.ConstraintSolver(automata_dict, settings)
        ans = cs.has_solution()
        if not ans:
            print cs.get_query()
        cs.constraint_gen.bounded_automata['receiver'].export(name='stutt')
        self.assertTrue(ans, 'Should be accepted!')
        
        
def get_number_of_vars(a, sem, bound):
    
    a_nodes = len(a.get_states())
    
    a_edges = a.get_transitions()
    send_edges= len([1 for _, _, d in a_edges if d['action'] == 'send'])
    rec_edges= len([1 for _, _, d in a_edges if d['action'] == 'receive'])
    eps_edges= len([1 for _, _, d in a_edges if d['action'] == 'eps'])
    if sem == 'multiset':
        # one var per node, and there are 2 copies of each node in each phase plus the final state 
        ret_num_nodes = 2 * bound * a_nodes + 1
        # one var per edge, and there are one edge per phase for each send and rec-edge in a,
        # two edges per phase for every eps-edge in a. Also, there are two edges per state in every
        # phase but the last, where there are only one edge per state
        # There is also an edge from every node to the new final state
        ret_num_edges = bound*(send_edges+rec_edges+2*eps_edges) + (2*bound-1)*a_nodes
        ret_num_edges += ret_num_nodes
        return ret_num_nodes + ret_num_edges
    elif sem == 'lossy':
        # one var per node, and there are 2 copies of each node in each phase 
        ret_num_nodes = 2 * bound * a_nodes
        assert False, "need to implement this!"
        # one var per edge, and there are one edge per phase for each send edge and two vars per
        # rec-edge in a, two edges per phase for every eps-edge in a. Also, there are two edges per
        # state in every phase but the last, where there are only one edge per state.
        ret_num_edges = bound*(send_edges+rec_edges+2*eps_edges) + (2*bound-1)*a_nodes + rec_edges
        return ret_num_nodes + ret_num_edges

def get_number_of_asserts(a, sem, bound):

    a_nodes = len(a.get_states())
    msg_alphabet = len(a.get_msg_alphabet())
    
    if sem == 'multiset':
        # there are 2 copies of each node in each phase 
        num_nodes = 2 * bound * a_nodes + 1
        
        ret_declaration_asserts = 0
        ret_node_asserts = 0
        ret_msg_asserts = 0
        # there is one assert for every variable declared
        ret_declaration_asserts += get_number_of_vars(a, sem, bound)
        # there is one consistency constraint per node
        ret_node_asserts += num_nodes
        # there are two enumeration constraint per node
        ret_node_asserts += 2*num_nodes
        # there is one constraint per phase, per message and channel.
        ret_msg_asserts += bound * msg_alphabet
        return ret_node_asserts + ret_msg_asserts + ret_declaration_asserts
#    elif sem == 'lossy': 
#        assert False
#        # one var per node, and there are 2 copies of each node in each phase 
#        ret_num_nodes = 2 * bound * a_nodes
#
#        # one var per edge, and there are one edge per phase for each send edge and two vars per
#        # rec-edge in a, two edges per phase for every eps-edge in a. Also, there are two edges per
#        # state in every phase but the last, where there are only one edge per state.
#        ret_num_edges = bound*(send_edges+rec_edges+2*eps_edges) + (2*bound-1)*a_nodes + rec_edges
#        return ret_num_nodes + ret_num_edges
    
#        # there is one copy of each send or receive edge for each phase,
#        # and two copies of each epsilon edge. There are also two edges added
#        # for each node in each phase but the last, where only one is added
#        # finally there is one eps-edge from every node to the new final state
#        a_edges = a.get_transitions()
#        send_edges= len([1 for _, _, d in a_edges if d['action'] == 'send'])
#        rec_edges= len([1 for _, _, d in a_edges if d['action'] == 'receive'])
#        eps_edges= len([1 for _, _, d in a_edges if d['action'] == 'eps'])
#        num_edges = bound * (send_edges + rec_edges + 2 * eps_edges)
#        num_edges += (2 * bound - 1) * a_nodes

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testConstraints']
    unittest.main()