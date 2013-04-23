'''
Created on Oct 11, 2012

@author: jonathan
'''
import subprocess
import time

class ConstraintSolver(object):
    
    num_asserts = 0
    def __init__(self, automata_dict, settings_dict):
        # We now have the original CPs in a dictionary automata_dict
        # where keys are role names and values are the individual CPs.
        # We can therefore now start the constraint generation.
        
        settings = settings_dict
        self.constraint_gen = ConstraintGenerator(automata_dict, settings['semantics'])
        
        bound = settings['bound']
        settings['bad_state'] = settings['role'] + '_' + settings['bad'] + '_R_' + str(bound)
        start = time.time()
        # TODO: The query is passed along in the settings dict. Make explicit.
        self.constraint_gen.generate(settings)
        self.constraint_generation_time = time.time() - start
        self.solver = Solver(settings)
        
    def has_solution(self):
        ans = self.solver.is_satisfiable()
        return ans
    
    def export_counter_example(self, prefix):
        assert False, 'Need to implement exporting of counter example'

    def get_query(self):
        return self.smt_query

class Solver(object):
    
    def __init__(self, settings):
        self.query_type = settings['query']
        if self.query_type == 'list':
            self.smt_command = settings['solver']
        elif self.query_type == 'file':
            self.tmp_file = settings['tmp_file']
            self.smt_command = settings['solver_from_file'] + ' ' + settings['tmp_file'] 
        elif self.query_type == 'simplest':
            self.smt_command = settings['solver']
        else:
            raise ValueError('Unknown query_type: ' + self.query_type)
        self.query = settings['_query']
        self.model = None

    def add_statement(self, smt_query):
        self.query += smt_query
    
    def get_query(self):
        return str(self.query)
    
    def finalize_query(self):
        if self.query_type == 'list' or self.query_type == 'simplest':
            self.proc=subprocess.Popen([self.smt_command, '-'], shell=True, 
                                       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE)
            start = time.time()
            res = self.proc.communicate(self.get_query())
            self.smt_time = time.time() - start
            return res
        elif self.query_type == 'file':
            self.query.finalize()
            start = time.time()
            self.proc=subprocess.Popen(self.smt_command,
                                       shell=True, 
                                       stdout=subprocess.PIPE)
            res = self.proc.communicate()
            self.smt_time = time.time() - start
            return res
        else: raise ValueError()
    
    def is_satisfiable(self):
        self.add_statement('(check-sat)')
        self.add_statement('(get-model)')
        self.answer, _ = self.finalize_query() 
        if self.answer.split('\n')[0].strip() == "sat":
            #self.model = parse_model(self.answer)
            return True
        elif self.answer.split('\n')[0].strip() == "unsat":
            return False
        raise ValueError('Strange answer from SMT solver: ' + self.answer)
    
    def get_var_val(self, var):
        return self.model[var]
    
    def get_vars(self):
        return self.model.keys()

def is_wellformed_statement(s):
    return s.count('(') == s.count(')')

def parse_model(model):
    var_dict = {}
    var_list = model.split('\n')[2:]
    i = 0
    while var_list[i].strip().startswith('('):
        key = var_list[i].split()[1].strip()
        val = int(var_list[i+1][:-1])
        var_dict[key] = val
        i += 2
    return var_dict


class ConstraintGenerator(object):
    '''
    Class that generates suitable constraints given a dictionary with automata
    '''

    def __init__(self, automata, semantics):
        '''
        Constructor
        '''
        self.automata = automata
        self.semantics = semantics
        self.bounded_automata = {}
    
    def generate(self, settings):
        
        query_type = settings['query']
        if query_type == 'list':
            query = ListQuery()
        elif query_type == 'file':
            tmp_file = settings['tmp_file']
            query = FileQuery(tmp_file)
        elif query_type == 'simplest':
            query = StringQuery()
        else:
            raise ValueError('Unknown query_type: ' + self.query_type)

        settings['_query'] = query
        bound = settings['bound']
        
        total_number_of_states = sum([len(a.get_states()) for a in self.automata.values()])
        print 'total # states: ' + str(total_number_of_states)
        start = time.time()
        print 'Generating bounded automata'
        for role in self.automata.keys():
            
            alt_aut = self.automata[role].get_k_alternating(bound, self.semantics,
                                                            total_number=total_number_of_states)
            self.bounded_automata[role] = alt_aut 
        
        self.b_total_number_of_states = sum([len(a.get_states()) for a in self.bounded_automata.values()])
        print 'total # states: ' + str(self.b_total_number_of_states)
        self.b_total_number_of_trans = sum([len(a.get_transitions()) for a in self.bounded_automata.values()])
        print 'total # transitions: ' + str(self.b_total_number_of_trans)
        
        lap = time.time() - start
        print 'Automata generation took ' + str(lap) + ' seconds'
        print 'Building P.I. for each automaton'
        start = time.time()
        # Now build Parikh Image for each graph
        for role in self.bounded_automata.keys():
            
            automaton = self.bounded_automata[role]
            initial_states = automaton.get_initial_states()
            if not len(initial_states) == 1:
                raise ValueError(role + ' does not have exactly 1 initial state')
            initial = initial_states[0]
            
            # Generate the channels
            if settings.has_key('prefix_channels') and settings['prefix_channels']:
                automaton.generate_channels(use_prefix=True)
            else:
                automaton.generate_channels()
            
            # Name the variables
            automaton.generate_vars()
            
            # Declare the variables
            query += generate_var_declarations(automaton, self.semantics)
            
            if role == settings['role']:
                # Isolate bad state
                final = role + '_' + settings['bad'] + '_R_' + str(bound)
            else:
                final_states = automaton.automaton.graph['final states']
                if not len(final_states) == 1:
                    raise ValueError(role + ' has not exactly one final state')
                final = final_states[0]
            simplepath = (self.semantics == 'lossy' or self.semantics == 'stuttering')
            query += generate_parikh_image_constraints(automaton,
                                                       initial, final,
                                                       simple_path=simplepath)
            
            # Ensure that any atomic send and receive are taken as meant to
            query += enforce_atomic_combined_send_receive(automaton.automaton)
        # end generate P.I.
        lap = time.time() - start
        print 'P.I. generation took ' + str(lap) + ' seconds'
        print 'Generating channel semantics constraints'
        start = time.time()
        
        if self.semantics == 'multiset':
            # Make sure the total number of messages sent in previous phases is less than or equal
            # to the number of messages consumed in all phases up to this one
            # This adds one constraint per message per phase
            query += '; adding message constraints\n'
            query += enforce_phase_ordering_on_messages([self.bounded_automata[role] for role in 
                                                         self.bounded_automata.keys()], bound)
        if self.semantics == 'lossy' or self.semantics == 'stuttering':
            query += '; adding global enumeration constraints\n'
            query += ensure_global_enum(self.bounded_automata, bound)
            
        if self.semantics == 'lossy':
            query += '; adding message constraints\n'
            query += enforce_receives_matches_specific_message([self.bounded_automata[role] for role in 
                                                                self.bounded_automata.keys()], bound)
            query += enforce_message_ordering_per_channel([self.bounded_automata[role] for role in 
                                                           self.bounded_automata.keys()])
        
        if self.semantics == 'stuttering':
            query += '; adding message constraints\n'
            query += enforce_receives_matches_specific_message([self.bounded_automata[role] for role in 
                                                                self.bounded_automata.keys()], bound)
            query += enforce_weak_message_ordering_per_channel([self.bounded_automata[role] for role in 
                                                                self.bounded_automata.keys()])
        
        lap = time.time() - start
        print 'Channel semantics constraint generation took ' + str(lap) + ' seconds'
        return query

class Query(object):
    '''
    Class that represents a query
    '''
    def __init__(self):
        pass
    
    def __add__(self, clause):
        raise NotImplementedError("Should have implemented this")

    def __iadd__(self, clause):
        raise NotImplementedError("Should have implemented this")


class StringQuery(Query):
    '''
    Class that represents the query as a string.
    '''
    def __init__(self):
        self.query = ''
        
    def __add__(self, arg):
        self.query += arg
    
    def __iadd__(self, arg):
        self.query += arg
        return self
    
    def __repr__(self):
        return self.query

class ListQuery(Query):
    '''
    Class that represents the query as a list of strings, and only concatenates if asked to.
    '''
    def __init__(self):
        self.query = []

    def __add__(self, clause):
        print 'add'
        self.query.append(clause)
        
    def __iadd__(self, clause):
        if isinstance(clause, self.__class__):
            self.query.extend(clause.query)
        else:
            self.query.append(clause)
        return self
    
    def count(self, word):
        sum([s.count('assert') for s in self.query])
    
    def __repr__(self):
        return ''.join(self.query)

class FileQuery(Query):
    '''
    Class that represents the query in a file.
    '''
    def __init__(self, tmp_file):
        self.tmp_file = tmp_file
        self.query = open(self.tmp_file, 'w')

    def __iadd__(self, clause):
        self.query.write(clause)
        return self
    
    def finalize(self):
        self.query.close()
    
def generate_var_declarations(aut, semantics):
    # Declare all variables
    # Also assert that each variable is greater than zero
    decls = ''
    decls += '; declaring e_vars \n'
    decls += build_declarations(aut.get_e_vars())
    decls += '; declaring f_vars \n'
    decls += build_declarations(aut.get_f_vars())
    if semantics == 'lossy' or semantics == 'stuttering':
        decls += '; declaring m_vars \n'
        decls += build_declarations(aut.get_m_vars())
    return decls
    
    
def generate_parikh_image_constraints(aut, init, final, simple_path=False):
    
    a = aut.automaton
    if not init in aut.get_states():
        raise ValueError('initial state not recognized: ' + init)
    if not final in aut.get_states():
        raise ValueError('final state not recognized: ' + final)

    # Build the Parikh image and store in p_img, start with empty string
    p_img = ''
    # add consistency constraints, handling initial state and final state in a special way
    # this adds two constraint per phase per state in the original automaton        
    p_img += '; adding consistency \n'
    for state in a.nodes():
        p_img += '; consistency of state ' + state + '\n'
        in_vars = aut.get_in_f_vars(state)
        out_vars = aut.get_out_f_vars(state)
        if state == init:
            p_img += '; Initial state constraint \n'
            p_img += build_assertion(build_statement('=',
                                                     build_sum(in_vars + ['1']),
                                                     build_sum(out_vars)))
        elif state == final:
            p_img += '; Final state constraint \n'
            p_img += build_assertion(build_statement('=', build_sum(in_vars),
                                                     build_sum(out_vars + ['1'])))
        else:
            p_img += build_assertion(build_statement('=', build_sum(in_vars),
                                                     build_sum(out_vars)))
        if simple_path:
            p_img += build_assertion(build_statement('<=', build_sum(in_vars), '1'))


    # ADD CONNECTEDNESS CONSTRAINTS
    #
    # The constraints are in two parts:
    # 1: we assert that for any node with some incoming or outgoing 
    #    edge that has a flow > 0, the e-var must be > 0.
    # 2: We let the e-var for the initial state be 1, and for each e-var e
    #    corresponding to a state s such that in(s) > 0, there needs
    #    to be a neighbor s' with corresponding e-var e' such that e' < e
    #    and |f_(s,s')| > 0
    #
    # Both of these points add one constraint per node, and since there are
    # two nodes per phase in the bounded alternation automaton, meaning in 
    # total there should be 4*bound*#nodes assertions in total   
    p_img += '; adding connectedness \n'
    for state, dct in a.nodes(data=True):
        # Bullet (1):
        p_img += '; connectedness constraint for state ' + state + '\n'
        edges_to_consider = a.in_edges(nbunch=[state], data=True)
        edges_to_consider.extend(a.out_edges(nbunch=[state], data=True))
        flow_vars = [d['f_var'] for _, _, d in edges_to_consider]
        flow_sum = build_sum(flow_vars)
        positive_flow = build_statement('>', flow_sum, '0')
        e_var = dct['e_var']
        positive_e_var = build_statement('>', e_var, '0')
        p_img += build_assertion(build_implication(positive_flow, positive_e_var))
        # Bullet (2):
        if state == init:
            p_img += build_assertion(build_statement('>=', e_var, '1'))
        else:
            in_flow_vars = [d['f_var'] for _, _, d in a.in_edges_iter(nbunch=[state], data=True)]
            in_flow_sum = build_sum(in_flow_vars)
            has_positive_in_flow = build_statement('>', in_flow_sum, '0')
            edges_to_consider = a.in_edges(nbunch=[state], data=True)
#            edges_to_consider.extend(a.out_edges(nbunch=[state], data=True))
            e_var_and_f_var_pairs = [(a.node[nbr]['e_var'],
                                      d['f_var']) for nbr, _, d in edges_to_consider]
            all_disjuncts = [build_statement('and',
                                             build_statement('>', f_var, '0'),
                                             build_statement('>', e_var, e_var_prime)) 
                             for e_var_prime, f_var in e_var_and_f_var_pairs]
            some_nbr_has_smaller_e_var = build_disjunction(all_disjuncts)
            p_img += build_assertion(build_implication(has_positive_in_flow,
                                                       some_nbr_has_smaller_e_var))
    return p_img

def ensure_global_enum(auts, bound):
    glob_enum = ''
    # For each phase, the e_vars should be different
    for i in range(bound):
        # pick an automaton A
        for a in auts.values():
            # Get the variables for phase i
            a_S_i_e_vars = a.get_e_vars_for_phase(i, 'S')
            a_R_i_e_vars = a.get_e_vars_for_phase(i, 'R')
            # and do for all other, call them B:s
            for b in auts.values():
                if not b is a:
                    # Isolate the e_vars from the same phase plus the previous sends
                    b_S_i_e_vars = b.get_e_vars_for_phase(i, 'S')
                    b_R_i_e_vars = b.get_e_vars_for_phase(i, 'R')
                    # For each pair of variables, one from A and one from B,
                    # enforce that they are different
                    for e_a in a_S_i_e_vars: 
                        for e_b in b_S_i_e_vars: 
                            equal = build_statement('=', e_a, e_b)
                            not_equal = negate(equal)
                            glob_enum += build_assertion(not_equal)
                    for e_a in a_R_i_e_vars: 
                        for e_b in b_R_i_e_vars: 
                            equal = build_statement('=', e_a, e_b)
                            not_equal = negate(equal)
                            glob_enum += build_assertion(not_equal)
                    if i > 0:
                        # For each phase, the e_vars should be larger than the e_vars of the
                        # previous phase for any other process
                        previous_b_R_i_e_vars = a.get_e_vars_for_phase(i-1, 'R')
                        for e_a in a_R_i_e_vars: 
                            for e_b in b_S_i_e_vars: 
                                is_larger = build_statement('<', e_b, e_a)
                                glob_enum += build_assertion(is_larger)
                        for e_a in a_S_i_e_vars:
                            for e_b in previous_b_R_i_e_vars:
                                is_larger = build_statement('<', e_b, e_a)
                                glob_enum += build_assertion(is_larger)
    return glob_enum

def enforce_path_simplicity(aut):
    simplicity = ''
    for node in aut.automaton.nodes():
        simplicity += build_assertion(build_statement('>=', '1',
                                                      build_sum(aut.get_in_f_vars(node))))
    return simplicity

def enforce_phase_ordering_on_messages(auts, bound):
    msgs = []
    for a in auts:
        msgs += a.get_msg_alphabet()
    msgs = list(set(msgs))
    sub_q = ''

    for msg in msgs:
        sum_vars_S = []
        sum_vars_R = []
        for phase in range(1, bound+1):
            for a in auts:
                sum_vars_S += a.get_f_vars_for_msg_in_phase(msg, phase, 'S')
                sum_vars_R += a.get_f_vars_for_msg_in_phase(msg, phase, 'R')
                sub_q += build_assertion(build_statement('>=',
                                                         build_sum(sum_vars_S),
                                                         build_sum(sum_vars_R)))
    return sub_q

def enforce_receives_matches_specific_message(auts, bound):
    ordered_messages = ''
    all_msgs = set()
    for aut in auts:
        all_msgs.update(aut.get_msg_alphabet())
    for msg in all_msgs:
        receives = []
        for aut in auts:
            receives += aut.get_f_var_m_var_e_var_triples_for_msg(msg)
        sends = []
        for aut in auts:
            sends += aut.get_f_var_e_var_pairs_for_send_of_msg(msg)
        for recv_trans in receives:
            recv_f, recv_m, recv_e = recv_trans
            msg_received = build_statement('>', recv_f, '0')
            disjuncts = []
            for send_trans in sends:
                send_f, send_e = send_trans
                is_matched = build_statement('=', recv_m, send_e)
                has_been_sent = build_statement('>', send_f, '0')
                happened_before = build_statement('<', send_e, recv_e)
                conjuncts = [is_matched, has_been_sent, happened_before]
                disjuncts += [build_conjunction(conjuncts)]
            some_send_matches = build_disjunction(disjuncts)
            ordered_messages += build_assertion(build_implication(msg_received, some_send_matches))
    return ordered_messages

def enforce_message_ordering_per_channel(auts):
    channels = {}
    for aut in auts:
        for k, v in aut.channels.iteritems():
            if not channels.has_key(k):
                channels[k] = v
            else:
                channels[k].update(v)
    # Just for sanity, check that there are no messages that goes to more than one channel
    for c, v in channels.iteritems():
        for c2, v2 in channels.iteritems():
            if not c == c2:
                assert v.isdisjoint(v2)
    
    enforcement = ''
    for _, msgs in channels.iteritems():
        rcvs = []
        for aut in auts:
            for msg in msgs:
                rcvs += aut.get_f_var_m_var_e_var_triples_for_msg(msg)
        # now we have all receives for a specific channel in the list rcvs.
        for f1, m1, e1 in rcvs:
            for f2, m2, e2 in rcvs:
                if not f1 == f2:
                    f1_pos = build_statement('>', f1, '0')
                    f2_pos = build_statement('>', f2, '0')
                    f1_after_f2 = build_statement('>', e1, e2)
                    both_used_and_1_after_2 = build_conjunction([f1_pos, f2_pos, f1_after_f2])
                    m1_sent_after_m2 = build_statement('>', m1, m2)
                    if_both_used_and_1_after_2_then_m1_sent_after_m2 = build_implication(both_used_and_1_after_2,
                                                                                         m1_sent_after_m2)
                    enforcement += build_assertion(if_both_used_and_1_after_2_then_m1_sent_after_m2)
    return enforcement

def enforce_weak_message_ordering_per_channel(auts):
    channels = {}
    for aut in auts:
        for k, v in aut.channels.iteritems():
            if not channels.has_key(k):
                channels[k] = v
            else:
                channels[k].update(v)
    # Just for sanity, check that there are no messages that goes to more than one channel
    for c, v in channels.iteritems():
        for c2, v2 in channels.iteritems():
            if not c == c2:
                assert v.isdisjoint(v2)
    
    enforcement = ''
    for _, msgs in channels.iteritems():
        rcvs = []
        for aut in auts:
            for msg in msgs:
                rcvs += aut.get_f_var_m_var_e_var_triples_for_msg(msg)
        # now we have all receives for a specific channel in the list rcvs.
        for f1, m1, e1 in rcvs:
            for f2, m2, e2 in rcvs:
                if not f1 == f2:
                    f1_pos = build_statement('>', f1, '0')
                    f2_pos = build_statement('>', f2, '0')
                    f1_after_f2 = build_statement('>', e1, e2)
                    both_used_and_1_after_2 = build_conjunction([f1_pos, f2_pos, f1_after_f2])
                    m1_sent_almost_after_m2 = negate(build_statement('<', m1, m2))
                    if_both_used_and_1_after_2_then_m1_sent_almost_after_m2 = build_implication(both_used_and_1_after_2,
                                                                                                m1_sent_almost_after_m2)
                    enforcement += build_assertion(if_both_used_and_1_after_2_then_m1_sent_almost_after_m2)
    return enforcement

def is_intermediate(state):
    return state.count('INTERMEDIATE_STATE') > 0

def enforce_atomic_combined_send_receive(a):
    
    # If we want an atomic send&receive, we can enforce that by the state enumeration, saying that
    # any intermediate state needs to have an enumerations number that is one less than its
    # successor (also an intermediate state, but in a different phase), which in turn needs to have
    # an enumeration number that is one less than its successor (the sink of the send transition)
    sub_q = ''
    intermediates = [state for state in a.nodes(data=True) if is_intermediate(state)]
    nexts = [a.successors(state) for state in intermediates]
    for i, n in zip(intermediates, nexts):
        if not len(n) == 1:
            raise ValueError(i + ' has more than one successor!')
        [nxt] = n
        e_i = a[i]['evar']
        e_n = a[nxt]['evar']
        e_i_gt_0 = build_statement('>', e_i, '0')
        impl = build_statement('=>', e_i_gt_0, build_statement('=', build_sum([e_i, '1']), e_n))
        sub_q += build_assertion(impl)
    return sub_q

def build_declarations(var_lst):
    return ''.join(['(declare-fun ' + var + ' () Int) \n' + \
                    build_assertion(build_statement('>=', var, '0')) for var in var_lst])

def build_sum(terms):
    ret_sum = ''
    for _ in terms:
        ret_sum += '(+ '
    ret_sum += '0 '
    for term in terms:
        ret_sum += term + ' ) '
    return ret_sum

def build_statement(cond, arg1, arg2):
    return '(' + cond + ' ' + arg1 + ' ' + ' ' + arg2 + ' )'

def build_assertion(statement):
    ConstraintSolver.num_asserts += 1
    return '(assert ' + statement + ' ) \n'

def build_implication(antecedent, consequent):
    return build_statement('=>', antecedent, consequent)

def build_disjunction(disjuncts):
    ret_or = ''
    for _ in disjuncts:
        ret_or += '(or '
    ret_or += 'false '
    for disjunct in disjuncts:
        ret_or += disjunct + ' ) '
    return ret_or

def build_conjunction(conjuncts):
    if not conjuncts:
        return 'true'
    return build_statement('and', conjuncts[0], build_conjunction(conjuncts[1:]))

def negate(statement):
    return build_statement('not', statement, '')