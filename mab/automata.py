'''
Created on Aug 6, 2012

@author: jonathan

This module defines the classes

CommunicatingProcess -
    An automaton that is deterministic except for epsilon transitions.
MABAutomaton -
    Stands for Mode Alternation Bounded Automaton, generates from a
    CommunicatingProcess DA an automaton MAB(DA) that only accepts the
    sub-language of L(DA) that has at most k alternations between read
    and write, for some given k. 
'''
import networkx
import networkx.algorithms.shortest_paths.generic as paths
#import subprocess

class CommunicatingProcess(object):
    '''
    A class representing an automaton with input and output. It is
    deterministic in the sense that there are never two transitions from 
    a state reading or writing the same message. This means that all
    non-determinism comes from epsilon transitions. 
    '''
  
    
    def __init__(self, name):
        '''
        Constructor
        '''
        self.automaton = networkx.MultiDiGraph()
        self.automaton.graph['initial states'] = []
        self.automaton.graph['final states'] = []
        self.epsilon_counter = 0
        self.automaton.graph['name'] = name
        
    def add_state(self, state):
      
        '''Adds state and ignores duplicates''' 
        self.automaton.add_node(state)
    
    def get_states(self):
        return self.automaton.nodes()
    
    def add_initial_state(self, state):
        if state not in self.automaton.graph['initial states']:
            self.automaton.graph['initial states'].append(state)
        
    def add_final_state(self, state):
        if state not in self.automaton.graph['final states']:
            self.automaton.graph['final states'].append(state)
        
    def get_initial_states(self):
        return self.automaton.graph['initial states']
        
    def add_transition(self, from_state, to_state, symbol, action):
      
        '''
        Since we want a deterministic automaton, we simply overwrite the old transition if there
        already is one from_state -> to_state. The string 'eps' represents epsilon transitions.
        '''
        if action and action not in ['send', 'receive', 'eps']:
            raise ValueError
        
        self.automaton.add_edge(from_state, to_state, symbol=symbol,
                                action=action, key=(action, symbol))
        
    def get_transitions(self, keys=False):
        return self.automaton.edges(data=True, keys=keys)
    
    def delete_sends(self):
        to_remove = [(f, t, dct) for f, t, dct in self.automaton.edges(data=True)
                     if dct['action'] == 'send']
        for trans in to_remove:
            f, t, d = trans
            self.automaton.remove_edge(f, t, key=(d['action'], d['symbol']))
        
    def delete_receives(self):
        to_remove = [(f, t, dct) for f, t, dct in self.automaton.edges(data=True)
                     if dct['action'] == 'receive']
        for trans in to_remove:
            f, t, d = trans
            self.automaton.remove_edge(f, t, key=(d['action'], d['symbol']))
    
        
    def get_next_state(self, current_state, action, symbol):
        '''
        current_state - the source of the transition
        action - whether we should send or receive
        symbol - the symbol to send or receive
        
        Returns a tuple (a, b) where a is the next state if we consume symbol through action
        or None if no such state exist, and b is a list of states containing all the states
        to which an epsilon transition can be made from current_transition.
        '''
        
        # Get next wrt action
        next_states = [t for f, t, d in self.automaton.edges(data=True)
                        if f == current_state and d['symbol'] == symbol and d['action'] == action]
                
        # Isolate possible epsilon steps
        eps = [t for f, t, d in self.automaton.edges(data=True)
               if f == current_state and d['symbol'] == 'eps']
        
        return next_states, eps
      
    def accepts_seq(self, start, seq, stop):
        
        '''seq is a list of (action * symbol) tuples'''
        if not seq:
            if start == stop:
                return start in self.automaton.nodes()
            _, epsilon_transitions = self.get_next_state(start, 'eps', 'eps')
        else:
            action, symbol = seq[0]
            states_after_symbol_consumed, epsilon_transitions = self.get_next_state(start, action,
                                                                                   symbol)
            for state in states_after_symbol_consumed:
                if self.accepts_seq(state, seq[1:], stop):
                    return True
        
        for state in epsilon_transitions:
            if self.accepts_seq(state, seq, stop):
                return True
        
        return False
    
    def get_copy(self):
        copy = CommunicatingProcess('')
        copy.automaton = self.automaton.copy()
        return copy
    
    def get_copy_named(self, name):
        copy = self.get_copy()
        copy.automaton.graph['name'] = name
        return copy
    
    def get_copy_suffixed(self, suffix):
        copy = self.get_copy()
        copy.automaton.graph['name'] = self.automaton.graph['name'] + suffix
        copy.automaton = networkx.relabel_nodes(copy.automaton, lambda x: x + suffix)
        return copy
    
    def get_send_phase_version(self, semantics, total_number=None):
            
        send_version = self.get_copy_named(self.automaton.graph['name'] + '_S')
        send_version.delete_receives()
        networkx.relabel_nodes(send_version.automaton, lambda x: x + '_S', copy=False)

        if semantics == 'lossy' or semantics == 'stuttering':        
        
            send_version.add_send_self_loops()
            send_version.unroll_send_self_loops(total_number)
        
        send_version.export(send_version.automaton.graph['name'])
        return send_version
    
    def get_receive_phase_version(self, semantics):
        
        receive_version = self.get_copy_named(self.automaton.graph['name'] + '_R')
        receive_version.delete_sends()
        networkx.relabel_nodes(receive_version.automaton, lambda x: x + '_R', copy=False)
        return receive_version

    def export(self, name=None, valuation=None):
        tmpdir = 'tmp/'
#        dotpgm = 'dot'
        filename = tmpdir + self.automaton.graph['name']
        if name:
            filename = tmpdir + name
        
        dotfile = filename + '.dot'
#        pngfile = filename + '.png'
        
        if valuation:
            # We now want to remove any edges that are not in the valuation 
            for fv, tv, key, dct in self.get_transitions(keys=True):
                if valuation.get_var_val(dct['f_var']) == 0:
                    self.automaton.remove_edge(fv, tv, key=key)
                else:
                    fvar = str(valuation.get_var_val(dct['f_var']))
                    self.automaton.edge[fv][tv][key]['label'] = fvar
            # Now we want to remove any orphaned nodes
            for node, deg in self.automaton.degree().iteritems():
                if deg == 0:
                    self.automaton.remove_node(node)
            
            
        networkx.write_dot(self.automaton, dotfile)

#        subprocess.call([dotpgm, '-T', 'png', '-o', pngfile, dotfile])
#        subprocess.call(['pwd'])
    
    def get_k_alternating(self, k, semantics, total_number):
        
        send_a = self.get_send_phase_version(semantics, total_number=k*total_number)
        rec_a = self.get_receive_phase_version(semantics)
        union = []
        # Make all copies for the union
        for i in range(1, k+1):
            union.append(send_a.get_copy_suffixed('_' + str(i)))
            union.append(rec_a.get_copy_suffixed('_' + str(i)))
        
        # Now we have all the disjoint copies, do the actual union
        union_automaton = union_all(union, self.automaton.graph['name'] +'_SR')
        
        # Make sure to keep the initial state, that has been renamed
        [old_initial] = self.automaton.graph['initial states']
        union_automaton.automaton.graph['initial states'] = [old_initial + '_S_1']
        
        # Now add the epsilon transitions
        for state in self.automaton.nodes():
            for i in range(1, k+1):
                union_automaton.add_transition(state + '_S_' + str(i),
                                               state + '_R_' + str(i), 'eps', 'eps')
            for i in range(1, k):
                union_automaton.add_transition(state + '_R_' + str(i),
                                               state + '_S_' + str(i+1), 'eps', 'eps')
        
        # Make sure to retain final state
        old_final = self.automaton.graph['final states']
        union_automaton.automaton.graph['final states'] = [old+'_R_'+str(k) for old in old_final]
        
        # Add a final state in such a way that any state becomes accepting
        union_automaton.make_all_states_accepting()
        return union_automaton
    
    def generate_vars(self):
        # Generate enumeration-variables
        for state in self.automaton.nodes():
            self.automaton.node[state]['e_var'] = 'e_' + state
        # Generate flow variables
        for source, target, d in self.automaton.edges(data=True):
            d['f_var'] = 'f_' + source + '_' + d['action'] + '_' + d['symbol'] + '_' + target
        # Generate matching variables
            if d['action'] == 'receive':
                d['m_var'] = 'm_' + source + '_' + d['action'] + '_' + d['symbol'] + '_' + target
        
    def get_in_f_vars(self, state):
        if not state in self.automaton.nodes():
            raise ValueError(state + ' not a valid state')
        return [d['f_var'] for _, t, d in self.automaton.edges(data=True) if t == state]

    def get_out_f_vars(self, state):
        if not state in self.automaton.nodes():
            raise ValueError(state + ' not a valid state')
        return [d['f_var'] for s, _, d in self.automaton.edges(data=True) if s == state]
    
    def get_f_vars_for_msg_in_phase(self, msg, phase, type_of_phase):
        if type_of_phase == 'S':
            suffix = 'S_' + str(phase)
            action = 'send'
        elif type_of_phase == 'R':
            suffix = 'R_' + str(phase)
            action = 'receive'
        return [d['f_var'] for _, _, d in self.automaton.edges(data=True) if
                d['action'] == action and d['symbol'] == msg and
                d['f_var'].endswith(suffix)]
        
    def get_e_vars_for_phase(self, phase, type_of_phase):
        if type_of_phase == 'S':
            suffix = 'S_' + str(phase)
        elif type_of_phase == 'R':
            suffix = 'R_' + str(phase)
        return [d['e_var'] for s, d in self.automaton.nodes(data=True) if s.endswith(suffix)]
    
    def get_e_vars(self):
        return [d['e_var'] for _, d in self.automaton.nodes(data=True)]
    
    def get_f_vars(self):
        return [d['f_var'] for _, _, d in self.automaton.edges(data=True)]
    
    def get_m_vars(self):
        return [d['m_var'] for _, _, d in self.automaton.edges(data=True) if d['action'] == 'receive']
    
    def get_f_var_e_var_pairs_for_send_of_msg(self, msg):
        # returns for every send transition a - c!m -> b the pair (flow_var, e_b)
        return [(d['f_var'], self.automaton.node[t]['e_var'])
                for _, t, d in self.get_transitions()
                if d['action']=='send' and d['symbol'] == msg]
    
    def get_f_var_m_var_e_var_triples_for_msg(self, msg):
        # returns for every receive transition a - c?m -> b the triple (flow_var, matching_var, e_b)
        return [(d['f_var'], d['m_var'], self.automaton.node[t]['e_var'])
                for _, t, d in self.get_transitions()
                if d['action']=='receive' and d['symbol'] == msg]
    
    def get_msg_alphabet(self):
        transition_data_set = set([d['symbol'] for _, _, d in self.get_transitions() 
                                   if (d['action'] in ['send', 'receive'])])
        return list(transition_data_set)
    
    def make_all_states_accepting(self):
        new_final_state = self.automaton.graph['name'][:-2] + 'ALL_STATES'
        self.add_state(new_final_state)
        for state in self.get_states():
            self.add_transition(state, new_final_state, 'eps', 'eps')
        self.automaton.graph['final states'] = [new_final_state]
        
    def generate_channels(self, use_prefix=False):
        self.channels = {}
        if use_prefix:
            msgs = self.get_msg_alphabet()
            for msg in msgs:
                if not self.channels.has_key(msg[0]):
                    self.channels[msg[0]] = set()
                self.channels[msg[0]].add(msg[1:])
            for n1, n2, key, d in self.automaton.edges(data=True, keys=True):
                new_symbol = (d['symbol'])[1:]
                self.automaton[n1][n2][key]['symbol'] = new_symbol
        else:
            self.channels[self.automaton.graph['name']] = set() 
            for d in (d for _, _, d in self.get_transitions() if d['action'] == 'send'):
                self.channels[self.automaton.graph['name']].add(d['symbol'])
                
    def get_channels(self):
        return self.channels
    
    def add_send_self_loops(self):
        if any([d['action'] == 'receive' for _, _, d in self.get_transitions()]):
            assert False, 'There should be no receive transitions!' 
        for state in self.automaton.nodes():
            for source, target, d in self.get_transitions():
                if d['action'] == 'send':
                    if paths.has_path(self.automaton, state, source):
                        if paths.has_path(self.automaton, target, state):
                            self.add_transition(state, state, d['symbol'], 'send')
    
    def unroll_send_self_loops(self, k):
        if any([d['action'] == 'receive' for _, _, d in self.get_transitions()]):
            assert False, 'There should be no receive transitions!' 
        states_with_self_loops = self.automaton.nodes_with_selfloops() 
        for state in states_with_self_loops:
            # add copies of the state
            for i in range(k):
                self.add_state(get_unroll_state(state, i))
            # isolate the self loop edge labels
            msgs = [d['symbol'] for s,_,d in self.automaton.selfloop_edges(data=True) if s == state]
            for i in range(k):
                if i is 0:
                    source = state
                else:
                    source = get_unroll_state(state, i-1)
                target = get_unroll_state(state, i)
                for msg in msgs:
                    self.add_transition(source, target, msg, 'send')
        # Remove the self loops from the graph
        self.automaton.remove_edges_from(self.automaton.selfloop_edges())
        # move the outgoing edges to the last copy
        for state in states_with_self_loops:
            out_trans = self.automaton.out_edges([state], keys=True, data=True)
            new_source = get_unroll_state(state, k-1)
            for s, t, key, d in out_trans:
                if not t == get_unroll_state(state, 0):
                    self.add_transition(new_source, t, d['symbol'], d['action'])
                    self.automaton.remove_edge(s, t, key=key) 

def union_all(union, name):
    res = CommunicatingProcess(name)
    a_set = [a.automaton for a in union]
    res.automaton = networkx.union_all(a_set)
    res.automaton.graph['name'] = name
    return res

def phase_suffix(state):
    # suffix is of form _[type of phase]_[index of phase]
    indicies_of_underscore = [i for i, _ in enumerate(state) if state[i] == '_']
    start_of_suffix = indicies_of_underscore[-1]
    return state[start_of_suffix:]

def state_without_phase_suffix(state):
    suffix = phase_suffix(state)
    return state[:-len(suffix)]

def get_unroll_state(state, i):
    unroll_state = state_without_phase_suffix(state) + '_unroll_' + str(i) + phase_suffix(state)
    return unroll_state