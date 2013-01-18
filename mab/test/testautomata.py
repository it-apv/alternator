'''
Created on Aug 6, 2012

@author: jonathan
'''
import unittest
import mab.automata
import mab.xml2automata
import mab.test.testtranslator

def get_sender_automaton():
    t = mab.xml2automata.Translator(mab.test.testtranslator.TestTranslator.abpinxml)
    return t.automata['SENDER']

def get_larger_automaton():
    # Here it should not work to reach s1 with order preserving
    # semantics, but should work with multiset
    a = mab.automata.CommunicatingProcess('foo')
    a.add_state('foo_s0')
    a.add_initial_state('foo_s0')
    a.add_state('foo_tmp')
    a.add_state('foo_tmp2')
    a.add_state('foo_tmp3')
    a.add_state('foo_s1')
    a.add_transition('foo_s0', 'foo_tmp', 'foo', 'send')
    a.add_transition('foo_tmp','foo_tmp2', 'bar', 'send')
    a.add_transition('foo_tmp2', 'foo_tmp3', 'bar', 'receive')
    a.add_transition('foo_tmp3', 'foo_s1', 'foo', 'receive')
#    a.add_transition('foo_s1', 'foo_s0', 'eps', 'eps')
    a.generate_vars()
    return a

def get_larger_automaton_2():
    # Here it should not work to reach s1 with bound 1, but should work
    # with bound >1
    a = mab.automata.CommunicatingProcess('foo')
    a.add_state('foo_s0')
    a.add_initial_state('foo_s0')
    a.add_state('foo_tmp')
    a.add_state('foo_tmp2')
    a.add_state('foo_tmp3')
    a.add_state('foo_s1')
    a.add_transition('foo_s0', 'foo_tmp', 'foo', 'send')
    a.add_transition('foo_tmp', 'foo_tmp2', 'foo', 'receive')
    a.add_transition('foo_tmp2','foo_tmp3', 'bar', 'send')
    a.add_transition('foo_tmp3', 'foo_s1', 'bar', 'receive')
#    a.add_transition('foo_s1', 'foo_s0', 'eps', 'eps')
    return a

def get_small_automaton_2():
    # Here it should work to reach s1
    a = mab.automata.CommunicatingProcess('foo')
    a.add_state('foo_s0')
    a.add_initial_state('foo_s0')
    a.add_state('foo_tmp')
    a.add_state('foo_s1')
    a.add_transition('foo_s0', 'foo_tmp', 'foo', 'send')
    a.add_transition('foo_tmp', 'foo_s1', 'foo', 'receive')
    a.add_transition('foo_s1', 'foo_s0', 'eps', 'eps')
    return a

def get_small_automaton_3():
    # Here it should not work to reach s1, because the messages are in the wrong order
    a = mab.automata.CommunicatingProcess('foo')
    a.add_state('foo_s0')
    a.add_initial_state('foo_s0')
    a.add_state('foo_tmp')
    a.add_state('foo_s1')
    a.add_transition('foo_s0', 'foo_tmp', 'foo', 'receive')
    a.add_transition('foo_tmp', 'foo_s1', 'foo', 'send')
    a.add_transition('foo_s1', 'foo_s0', 'eps', 'eps')
    return a

def get_small_automaton():
    # Here it should not work to reach s1 because the messages are different
    a = mab.automata.CommunicatingProcess('foo')
    a.add_state('foo_s0')
    a.add_initial_state('foo_s0')
    a.add_state('foo_tmp')
    a.add_state('foo_s1')
    a.add_transition('foo_s0', 'foo_tmp', 'foo', 'send')
    a.add_transition('foo_tmp', 'foo_s1', 'bar', 'receive')
    a.add_transition('foo_s1', 'foo_s0', 'eps', 'eps')
    return a

def get_tricky_automaton():
    # This should not work if the flow is connected, but it should work otherwise.
    a = mab.automata.CommunicatingProcess('tricky')
    a.add_state('tricky_a')
    a.add_initial_state('tricky_a')
    a.add_state('tricky_b')
    a.add_state('tricky_c')
    a.add_transition('tricky_a', 'tricky_b', 'bar', 'receive')
    a.add_transition('tricky_a', 'tricky_c', 'eps', 'eps')
    a.add_transition('tricky_c', 'tricky_c', 'bar', 'send')
    a.export()
    return a

def get_channel_prefixed_automaton():
    # This should not work if the flow is connected, but it should work otherwise.
    a = mab.automata.CommunicatingProcess('channel_prefixed')
    a.add_state('tricky_a')
    a.add_initial_state('tricky_a')
    a.add_state('tricky_b')
    a.add_state('tricky_c')
    a.add_state('tricky_d')
    a.add_state('tricky_e')
    a.add_transition('tricky_a', 'tricky_b', 'Abar', 'receive')
    a.add_transition('tricky_a', 'tricky_c', 'Abar', 'send')
    a.add_transition('tricky_c', 'tricky_c', 'Abar', 'receive')
    a.add_transition('tricky_b', 'tricky_d', 'Bbar', 'send')
    a.add_transition('tricky_d', 'tricky_e', 'Bbar', 'receive')
    return a

def get_msg_sender(name, msg):
    a = mab.automata.CommunicatingProcess(name)
    state1 = name + '_1'
    state2 = name + '_2'
    a.add_state(state1)
    a.add_state(state2)
    a.add_initial_state(state1)
    a.add_final_state(state2)
    a.add_transition(state1, state2, msg, 'send')
    return a
    
def get_linear_msg_sender(name, msg, num_of_transitions):
    a = mab.automata.CommunicatingProcess(name)
    a.add_state(name)
    a.add_initial_state(name)
    previous_state = name
    state = name
    for i in range(num_of_transitions):
        state = name + '_' + str(i)
        a.add_state(state)
        a.add_transition(previous_state, state, msg, 'send')
        previous_state = state
    a.add_final_state(state)
    return a
    
def get_msg_receiver(name, msg):
    a = mab.automata.CommunicatingProcess(name)
    state1 = name + '_1'
    state2 = name + '_2'
    a.add_state(state1)
    a.add_state(state2)
    a.add_initial_state(state1)
    a.add_final_state(state2)
    a.add_transition(state1, state2, msg, 'receive')
    return a

def get_linear_msg_receiver(name, msg, num_of_transitions):
    a = mab.automata.CommunicatingProcess(name)
    a.add_state(name)
    a.add_initial_state(name)
    previous_state = name
    state = name
    for i in range(num_of_transitions):
        state = name + '_' + str(i)
        a.add_state(state)
        a.add_transition(previous_state, state, msg, 'receive')
        previous_state = state
    a.add_final_state(state)
    return a
    
def get_looping_send_automaton():
    a = mab.automata.CommunicatingProcess('big_looping_send')
    a.add_state('A_S')
    a.add_initial_state('A_S')
    a.add_state('B_S')
    a.add_state('C_S')
    a.add_state('D_S')
    a.add_transition('A_S', 'B_S', 'a', 'send')
    a.add_transition('B_S', 'C_S', 'b', 'send')
    a.add_transition('C_S', 'A_S', 'c', 'send')
    a.add_transition('B_S', 'D_S', 'd', 'send')
    a.add_transition('D_S', 'D_S', 'e', 'send')
    return a

def get_small_looping_send_automaton():
    a = mab.automata.CommunicatingProcess('small_looping_send')
    a.add_state('A_S')
    a.add_initial_state('A_S')
    a.add_state('B_S')
    a.add_transition('A_S', 'B_S', 'a', 'send')
    a.add_transition('B_S', 'A_S', 'b', 'send')
    return a

class TestAutomaton(unittest.TestCase):

    def test_automaton_init(self):
        a = mab.automata.CommunicatingProcess('FOO!')
        self.assertEqual(a.get_states(), [], 'Faulty states set initialization')
        self.assertEqual(a.get_initial_states(), [], 'Faulty initial states initialization')
        self.assertEqual(a.get_transitions(), [], 'Faulty transitions initialization')

    def test_add_state(self):
        a = mab.automata.CommunicatingProcess('FOO!')
        a.add_state('foo_s0')
        self.assertEqual(a.get_states(), ['foo_s0'], 'Addition of state not working!')

    def test_add_initial_state(self):
        a = mab.automata.CommunicatingProcess('FOO!')
        a.add_initial_state('foo_s0')
        self.assertEqual(a.get_initial_states(), ['foo_s0'],
                         'Addition of initial state not working!')

    def test_add_transition(self):
        a = get_small_automaton()
        self.assertIn(('foo_s0', 'foo_tmp', {'action': 'send', 'symbol': 'foo'}),
                      a.get_transitions(), 'Did not find transitions in dict!')
        self.assertIn(('foo_tmp', 'foo_s1', {'action': 'receive', 'symbol': 'bar'}),
                      a.get_transitions(), 'Did not find transitions in dict!')
      
    def test_delete_sends(self):
        a = get_small_automaton()
        self.assertIn(('foo_s0', 'foo_tmp', {'action': 'send', 'symbol': 'foo'}),
                      a.get_transitions(), 'Did not find transitions in dict!')
        self.assertIn(('foo_tmp', 'foo_s1', {'action': 'receive', 'symbol': 'bar'}),
                      a.get_transitions(), 'Did not find transitions in dict!')
        self.assertEqual(len(a.get_transitions()), 3, 'there should be two transitions')
        a.delete_sends()
        self.assertTrue(('foo_s0', 'foo_tmp',
                         {'action': 'send', 'symbol': 'foo'}) not in a.get_transitions(),
                        'there should be no send transitions!')
        self.assertIn(('foo_tmp', 'foo_s1', {'action': 'receive', 'symbol': 'bar'}),
                      a.get_transitions(), 'Did not find transitions in dict!')
        self.assertEqual(len(a.get_transitions()), 2, 'there should be two transitions')

    def test_delete_receives(self):
        a = get_small_automaton()
        self.assertIn(('foo_s0', 'foo_tmp', {'action': 'send', 'symbol': 'foo'}),
                      a.get_transitions(),
                      'Did not find transitions in dict!')
        self.assertIn(('foo_tmp', 'foo_s1', {'action': 'receive', 'symbol': 'bar'}),
                      a.get_transitions(),
                      'Did not find transitions in dict!')
        self.assertEqual(len(a.get_transitions()), 3, 'there should be two transitions')
        a.delete_receives()
        self.assertIn(('foo_s0', 'foo_tmp', {'action': 'send', 'symbol': 'foo'}),
                      a.get_transitions(),
                      'there should be a send transitions!')
        self.assertTrue(('foo_tmp', 'foo_s1',
                         {'action': 'receive', 'symbol': 'bar'}) not in a.get_transitions(),
                        'Found transitions in dict!')
        self.assertEqual(len(a.get_transitions()), 2, 'there should be two transitions')
      
    def test_get_next_state(self):
        a = get_sender_automaton()
        self.assertEqual(a.get_next_state('SENDER_Q2', 'send', 'mesg1'), (['SENDER_Q3'],[]),
                         'Found wrong next state!')
      
    def test_accepts_seq(self):
        a = get_sender_automaton()
        self.assertTrue(a.accepts_seq('SENDER_Q0', [], 'SENDER_Q0'),
                        'Should accept empty string if start and stop are the same!')
        self.assertTrue(a.accepts_seq('SENDER_Q3', [], 'SENDER_Q3'),
                        'Should accept empty string if start and stop are the same!')
        self.assertTrue(not a.accepts_seq('SENDER_Q0', [], 'SENDER_Q1'),
                        'Should not accept empty string if start and stop are different!')
        self.assertTrue(not a.accepts_seq('foo!', [], 'foo!'),
                        'Should not accept empty string if start and stop are not states!')
      
    def test_accepts_seq_2(self):
        a = get_sender_automaton()
        a.add_transition('SENDER_Q0', 'SENDER_Q2', 'eps', 'eps')
        a.add_transition('SENDER_Q1', 'SENDER_Q2', 'eps', 'eps')
      
        # Test easy sequence
        self.assertTrue(a.accepts_seq('SENDER_Q0',
                                      [('send', 'mesg0'), ('send', 'mesg0'), ('send', 'mesg0')],
                                        'SENDER_Q1'),
                        'should accept this sequence!')
        # Test another easy sequence
        self.assertTrue(a.accepts_seq('SENDER_Q2',
                                      [('send', 'mesg1'), ('send', 'mesg1'),
                                       ('receive', 'ack0'), ('send', 'mesg1')],
                                       'SENDER_Q3'),
                        'should accept this sequence!')
        # Test run that ends up in the wrong state
        self.assertTrue(not a.accepts_seq('SENDER_Q4', [('send', 'mesg0'), ('send', 'mesg0'),
                                                        ('send', 'mesg0')],
                                          'SENDER_Q0'),
                        'should not accept this sequence!')
        # Test run that get nowhere before consuming whole string
        self.assertTrue(not a.accepts_seq('SENDER_Q0',
                                          [('send', 'mesg0'), ('send', 'mesg1'), ('send', 'mesg0')],
                                          'SENDER_Q1'),
                        'should not accept this sequence!')
        # Test run that requires epsilon transition at the start
        self.assertTrue(a.accepts_seq('SENDER_Q0', [('send', 'mesg1'), ('send', 'mesg1'),
                                                    ('receive', 'ack0'), ('send', 'mesg1')],
                                      'SENDER_Q3'),
                        'should accept this sequence!')
        # Test run that requires epsilon transition in the middle
        self.assertTrue(a.accepts_seq('SENDER_Q0', [('send', 'mesg0'), ('send', 'mesg1'),
                                                    ('receive', 'ack0'), ('send', 'mesg1')],
                                      'SENDER_Q3'),
                        'should accept this sequence!')
        # Test sequence that ends with an epsilon transition
        self.assertTrue(a.accepts_seq('SENDER_Q0',
                                      [('send', 'mesg0'), ('send', 'mesg0'), ('send', 'mesg0')],
                                      'SENDER_Q2'),
                        'should accept this sequence!')
        
    def test_accepts_seq_3(self):
        a = get_small_looping_send_automaton()
        self.assertTrue(a.accepts_seq('A_S', [('send', 'a')], 'B_S'), 'Should accept just send a')
        self.assertFalse(a.accepts_seq('A_S', [('send', 'a'), ('send', 'a'), ('send', 'a')], 'B_S'),
                         'Should not accept just send a:s')
        self.assertTrue(a.accepts_seq('A_S', [('send', 'a'), ('send', 'b'), ('send', 'a')], 'B_S'),
                        'Should accept alternating a:s and b:s')
        
    def test_copy(self):
        a = get_sender_automaton()
        copy_of_a = a.get_copy()
        a.add_transition('SENDER_Q0', 'SENDER_Q2', 'eps', 'eps')
        copy_of_a.add_state('foo')
        self.assertEqual(a.get_next_state('SENDER_Q0', 'send', 'mesg0'),
                         (['SENDER_Q1'], ['SENDER_Q2']), 'There should be two next states!')
        self.assertEqual(copy_of_a.get_next_state('SENDER_Q0', 'send', 'mesg0'),
                         (['SENDER_Q1'], []), 'There should be only one next state!')
        self.assertEqual(len(a.get_states()) + 1, len(copy_of_a.get_states()),
                         'The state set should not be altered in a!')

    def test_get_k_alternating_multiset(self):
        a = get_small_automaton()
        a_2 = a.get_k_alternating(2, 'multiset', len(a.get_states()))
        self.assertEqual(len(a_2.automaton.nodes()), 13)
        self.assertEqual(len(a_2.automaton.edges()), 30)
        
    def test_get_k_alternating_lossy(self):
        a = get_small_looping_send_automaton()
        a_2 = a.get_k_alternating(2, 'lossy', len(a.get_states()))
        a_2.export()
        self.assertEqual(len(a_2.automaton.nodes()), 25)
        self.assertEqual(len(a_2.automaton.edges()), 18*2+6+25)
        
    def test_generate_vars(self):
        a = get_small_automaton() # Has 3 nodes
        a_3 = a.get_k_alternating(3, 'multiset', len(a.get_states()))
        a_3.generate_vars()
        e_vars = [d['e_var'] for _, d in a_3.automaton.nodes(data=True)]
        # e_vars should have 19 entries, 3*2 per phase and one extra final state
        self.assertEqual(len(e_vars), 3*2*3+1)
        self.assertIn('e_foo_s0_S_1', e_vars)
        self.assertIn('e_foo_tmp_R_3', e_vars)
        f_vars = [d['f_var'] for _, _, d in a_3.automaton.edges(data=True)]
        # f_vars should have 3 send entries, 3 receive entries, and 6+15+19 eps-entries
        self.assertEqual(len(f_vars), 3+3+6+15+19)
        self.assertIn('f_foo_tmp_S_1_eps_eps_foo_tmp_R_1', f_vars)
        self.assertIn('f_foo_s1_R_3_eps_eps_foo_s0_R_3', f_vars)
        
    def test_get_in_f_vars(self):
        a = get_small_automaton().get_k_alternating(3, 'multiset',
                                                    len(get_small_automaton().get_states()))
        a.generate_vars()
        self.assertItemsEqual(a.get_in_f_vars('foo_s0_R_2'), ['f_foo_s0_S_2_eps_eps_foo_s0_R_2',
                                                          'f_foo_s1_R_2_eps_eps_foo_s0_R_2'])
        self.assertEqual(len(a.get_in_f_vars('foo_s0_R_1')), 2)
        self.assertIn('f_foo_s1_R_3_eps_eps_foo_s0_R_3', a.get_in_f_vars('foo_s0_R_3'))
        
    def test_get_out_f_vars(self):
        a = get_small_automaton().get_k_alternating(3, 'multiset',
                                                    len(get_small_automaton().get_states()))
        a.generate_vars()
        self.assertItemsEqual(a.get_out_f_vars('foo_s0_R_2'),
                              ['f_foo_s0_R_2_eps_eps_foo_s0_S_3',
                               'f_foo_s0_R_2_eps_eps_foo_ALL_STATES'])
        self.assertIn('f_foo_s0_S_3_send_foo_foo_tmp_S_3', a.get_out_f_vars('foo_s0_S_3'))
        
    def test_get_out_f_vars_2(self):
        a = get_larger_automaton().get_k_alternating(3, 'multiset',
                                                     len(get_larger_automaton().get_states()))
        a.generate_vars()
        self.assertItemsEqual(a.get_out_f_vars('foo_s0_R_2'),
                              ['f_foo_s0_R_2_eps_eps_foo_s0_S_3',
                               'f_foo_s0_R_2_eps_eps_foo_ALL_STATES'])
        self.assertEqual(len(a.get_out_f_vars('foo_s0_R_1')), 2)
        self.assertIn('f_foo_s0_S_3_send_foo_foo_tmp_S_3', a.get_out_f_vars('foo_s0_S_3'))
        
    def test_get_f_vars_for_msg_in_phase(self):
        a = get_small_automaton().get_k_alternating(3, 'multiset',
                                                    len(get_small_automaton().get_states()))
        a.generate_vars()
        self.assertEqual(a.get_f_vars_for_msg_in_phase('foo', 3, 'S'),
                         (['f_foo_s0_S_3_send_foo_foo_tmp_S_3']))
        self.assertEqual(a.get_f_vars_for_msg_in_phase('bar', 1, 'R'),
                         (['f_foo_tmp_R_1_receive_bar_foo_s1_R_1']))
        
    def test_get_msg_alphabet(self):
        a = get_small_automaton()
        self.assertItemsEqual(['foo', 'bar'], a.get_msg_alphabet(), 'The alphabet is not correct!')
        
    def test_isolate_prefix_channels(self):
        a = get_channel_prefixed_automaton()
        a.generate_channels(use_prefix=True)
        channels = a.get_channels()
        self.assertDictEqual(channels, {'A': set(['bar']), 'B': set(['bar'])},
                             str(channels) +' is not the correct channels!')
        msgs = a.get_msg_alphabet()
        self.assertIn('bar', msgs, '\'bar\' should be in ' + str(msgs))
        
    def test_add_self_loops(self):
        a = get_looping_send_automaton()
        self.assertEqual(len(a.get_transitions()), 5, 'Should be five transitions initially')
        a.add_send_self_loops()
        self.assertEqual(len(a.get_transitions()), 14, 'Should be 14 transitions after adding self loops')
        
    def test_add_self_loops_2(self):
        a = get_small_looping_send_automaton()
        self.assertEqual(len(a.get_transitions()), 2, 'Should be two transitions initially')
        a.add_send_self_loops()
        self.assertEqual(len(a.get_transitions()), 6, 'Should be six transitions after adding self loops')
        
    def test_add_self_loops_3(self):
        a = get_larger_automaton_2()
        a.delete_receives()
        self.assertEqual(len(a.get_transitions()), 2, 'Should be two transitions initially')
        a.add_send_self_loops()
        self.assertEqual(len(a.get_transitions()), 2, 'Should still be two transitions after adding self loops')
        
    def test_unroll_send_self_loops(self):
        a = get_looping_send_automaton()
        a.add_send_self_loops()
        self.assertEqual(len(a.get_transitions()), 14, 'Should be 14 transitions after adding self loops')
        a.unroll_send_self_loops(4)
        self.assertEqual(len(a.get_transitions()), 44, 
                         'Should be 44 transitions after unrolling self loops, not ' + str(len(a.get_transitions())))
        
    def test_unroll_send_self_loops_2(self):
        k = 3
        a = get_small_looping_send_automaton()
        self.assertTrue(a.accepts_seq('A_S', [('send', 'a')], 'B_S'), 'Should accept just one a!')
        self.assertFalse(a.accepts_seq('A_S', [('send', 'a'), ('send', 'a')], 'B_S'), 'Should not accept two a:s!')
        self.assertTrue(a.accepts_seq('A_S', [('send', 'a'), ('send', 'b')], 'A_S'), 'Should accept ab!')
        a.add_send_self_loops()
        self.assertTrue(a.accepts_seq('A_S', [('send', 'a')], 'B_S'), 'Should accept just one a!')
        self.assertTrue(a.accepts_seq('A_S', [('send', 'a'), ('send', 'a')], 'A_S'), 'Should now accept two a:s!')
        self.assertTrue(a.accepts_seq('A_S', [('send', 'a'), ('send', 'b')], 'A_S'), 'Should accept ab!')
        self.assertEqual(len(a.get_transitions()), 6, 'Should be 6 transitions after adding self loops')
        a.unroll_send_self_loops(k)
        self.assertEqual(len(a.get_transitions()), 14, 
                         'Should be 14 transitions after unrolling self loops, not ' + str(len(a.get_transitions())))
        self.assertFalse(a.accepts_seq('A_S', [('send', 'a')], 'B_S'), 'Should no longer accept just one a!')
        self.assertTrue(a.accepts_seq('A_S', [('send', 'a'),('send', 'a'),('send', 'a'),('send', 'a')], 'B_S'),
                         'Should accept k+1 a:s!')
        
    def test_unroll_send_self_loops_3(self):
        a = get_larger_automaton_2()
        a.delete_receives()
        self.assertEqual(len(a.get_transitions()), 2, 'Should be two transitions initially')
        a.add_send_self_loops()
        self.assertEqual(len(a.get_transitions()), 2, 'Should still be two transitions after adding self loops')
        a.unroll_send_self_loops(1000)
        self.assertEqual(len(a.get_transitions()), 2,
                         'Should still be two transitions after unrolling self loops, as there are none')
        
    def test_get_k_alternating(self):
        a = get_larger_automaton_2()
        a_send = a.get_send_phase_version('lossy', 10000)
        self.assertEqual(len(a.get_states()), len(a_send.get_states()),
                         'There should be no extra states, because there are no loops')
        
        
    def test_unroll_send_self_loops_4(self):
        a = get_larger_automaton_2()
        a_alt = a.get_k_alternating(2, 'lossy', len(a.get_states()))
        self.assertEqual(len(a_alt.get_states()), 21, 'should be 21 states, no unroll necessary!')
        
    def test_get_k_alternating_2(self):
        a = get_small_looping_send_automaton()
        a_alt = a.get_k_alternating(2, 'lossy', 3)
        self.assertTrue(a_alt.accepts_seq('A_S_S_1', [('send', 'a')]*7, 'B_S_S_1'), 'Should accept sequence!')
        
if __name__ == '__main__':
    unittest.main()