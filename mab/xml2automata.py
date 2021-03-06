'''
Created on Aug 3, 2012

@author: jonathan
'''
from xml.dom.minidom import parseString
import mab.automata

class Translator(object):
    '''
    classdocs
    
    A simple parser for protocols generated by the csv2xml.sh script
    
    After 'parse' and 'generate_automata' are called, the class has a
    dictionary called automata, that contains all the automata described
    in the input xml document. More specifically, the keys of the dict
    are the names of each role, and the value is an automaton in the
    following format, very much similar to a standard Kripke structure:
    
    {
    'states': STATE_SET (list of string)
    'initial': SUBSET_OF_STATE_SET (list of string)
    'transitions': SET_OF_TRANSITIONS (list of string*type*symbol*string)
    }
    
    '''
  
    
    def __init__(self, xml):
        '''
        Constructor
        '''
        self.intermediate_counter = 0
        # Build the DOM tree
        dom_built = self.parse(xml)
        assert dom_built, 'Faulty xml input, not able to build DOM!'
        # Convert into graph representation
        self.generate_automata()
        
    def parse(self, data):
        '''
        Parses the protocol in data and stores it in self.dom.
        Does elementary checking for faulty input.
        Does NOT validate against schema.
        '''
        
        try:
            protocol_dom = parseString(data)
        except:
            return False
        
        if not protocol_dom.documentElement.tagName == 'protocol':
            return False
        else:
            self.dom = protocol_dom
            return True
        
    def generate_automata(self):
        self.automata = {}
        for current_role in self.dom.getElementsByTagName('role'):
            name = current_role.getAttribute('name')
            if not name:
                raise LookupError('Found no name for role!')
            automaton = mab.automata.CommunicatingProcess(name)
            
            for state in current_role.getElementsByTagName('state'):
                statename = build_name(str(name), str(state.firstChild.nodeValue))
                automaton.add_state(statename)
                if state.hasAttribute('type') and \
                    state.getAttribute('type') == 'initial':
                    automaton.add_initial_state(statename)
                if state.hasAttribute('type') and \
                    state.getAttribute('type') == 'final':
                    automaton.add_final_state(statename)
                    
            # END ADDING STATES
            
            for trans in current_role.getElementsByTagName('rule'):
                from_state = build_name(str(name),
                                        trans.getElementsByTagName('current_state')[0].firstChild.nodeValue)
                to_state = build_name(str(name), 
                                      trans.getElementsByTagName('next_state')[0].firstChild.nodeValue)
                if trans.getElementsByTagName('send_message'):
                    send_symbol = trans.getElementsByTagName('send_message')[0].firstChild.nodeValue
                else:
                    send_symbol = ''
                if trans.getElementsByTagName('received_message'):
                    receive_symbol = trans.getElementsByTagName('received_message')[0].firstChild.nodeValue
                else:
                    receive_symbol = ''
                
                if send_symbol =='' and (receive_symbol == '' or receive_symbol == 'eps'):
                    # epsilon transition
                    automaton.add_transition(from_state, to_state, 'eps', 'eps')
                elif receive_symbol == '':
                    # send transition, no intermediate state
                    automaton.add_transition(from_state, to_state, send_symbol, 'send')
                elif send_symbol == '':
                    # receive transition, no intermediate state
                    automaton.add_transition(from_state, to_state, receive_symbol, 'receive')
                else:
                    # Both send and receive, so we need an intermediate state
                    # We use name of transition
                    
                    intermediate_state = build_name(str(name), 'INTERMEDIATE_STATE_' + trans.getAttribute('id'))
                    if intermediate_state.count('INTERMEDIATE_STATE') > 1:
                        raise ValueError(name + ' contains forbidden string "INTERMEDIATE_STATE"')
                    
                    automaton.add_state(intermediate_state)
                    automaton.add_transition(from_state, intermediate_state, receive_symbol, 'receive')
                    automaton.add_transition(intermediate_state, to_state, send_symbol, 'send')
                
            # END ADDING TRANSITIONS
            
            if  len(automaton.automaton.graph['final states']) > 1:
                final_state = automaton.automaton.graph['name'] + 'FINAL_STATE'
                for state in automaton.automaton.graph['final states']:
                    automaton.add_transition(state, final_state, "eps", "eps")
                automaton.automaton.graph['final states'] = [final_state]
      
            self.automata[name] = automaton
          
        # END ADDING AUTOMATA (by role)
        
        self.messages = []
        for message in self.dom.getElementsByTagName('message'):
            self.messages = message.firstChild.nodeValue
    
        # SANITY CHECK MESSAGES
        # Check that each message is only sent by one role
        # and received by one role. Not necessary really but
        # makes us able to forget about channels.
        action_symbol_pairs = []
        for a in self.automata.values():
            this_automatons_action_symbol_pairs = []
            for _, _, d in a.automaton.edges(data=True):
                if not d['symbol'] == 'eps':
                    pair = (d['action'], d['symbol'])
                    if not pair in this_automatons_action_symbol_pairs:
                        this_automatons_action_symbol_pairs.append(pair)
            for pair in this_automatons_action_symbol_pairs:
                if pair in action_symbol_pairs:
                    raise ValueError(str(pair) + ' is being sent or received by two different roles')
            
#            print 'Operations by ' + role + ': ' + str(sorted(this_automatons_action_symbol_pairs))
#            action_symbol_pairs += this_automatons_action_symbol_pairs    
#            a.export()
    
    def has_role(self, role):
        return self.automata.has_key(role)
    
    def get_automata(self):
        return self.automata
    
def build_name(role, name):
    return str(role) + '_' + str(name)