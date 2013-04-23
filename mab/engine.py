'''
Created on Dec 8, 2012

@author: jonathan
'''
import mab.xml2automata
import mab.constraints

class Engine(object):
    '''
    Class that makes everything go together
    '''

    def __init__(self, settings_file_path, arg_dict):
        '''
        Constructor
        '''
        self.parse_settings(settings_file_path, arg_dict)
        
        xmlfile = open(self.settings['file'])
        xmlstring = xmlfile.read()
        xmlfile.close()
    
        trans = mab.xml2automata.Translator(xmlstring)
        assert trans.has_role(self.settings['role'])
        
        role_to_automata_dict = trans.get_automata()
        settings_dict = self.settings
        
        self.cs = mab.constraints.ConstraintSolver(role_to_automata_dict, settings_dict)
        
    
    def parse_settings(self, settings_file_path, arg_dict):
        settings_file = open(settings_file_path)
        self.settings = {}
        
        # Parse the settings file, store in dict
        for line in settings_file:
            if not line.startswith('#'):
                split_line = line.strip().split(' ', 1)
                self.settings[split_line[0]] = split_line[1]
            
        settings_file.close()
        
        # Overwrite any settings from the settings file with the ones given from the command line
        for k, v in arg_dict.iteritems():
            if v is not None and v is not 0:
                self.settings[k] = v
        self.settings['bound'] = int(self.settings['bound'])
        
        print self.settings
        
        assert self.settings.has_key('file'), 'Aborting: No protocol file specified'
        assert self.settings.has_key('bound'), 'No bound given!'
        assert self.settings.has_key('bad'), 'Name of bad state not given!'
        assert self.settings.has_key('role'), 'Name of role with bad state not given!'

    
    def has_solution(self):
        return self.cs.has_solution()
    
    
    def export_counter_example(self, prefix):
        return self.cs.export_counter_example(prefix)
    
    def get_smt_time(self):
        return self.cs.solver.smt_time
    
    def get_constraint_generation_time(self):
        return self.cs.constraint_generation_time