#! /Library/Frameworks/Python.framework/Versions/2.7/bin/python

'''
Created on Aug 3, 2012

@author: jonathan
'''
import argparse
import mab.engine
import time

def print_table(total, engine, settings, result):

    name_dict = {'examples/STP.xml': '\\textsc{stp}',
                 'examples/BAwCC.xml': '\\textsc{cc}',
                 'examples/EnhancedBAwCC.xml': '\\textsc{cc}v2',
                 'examples/BAwPC.xml': '\\textsc{pc}',
                 'examples/EnhancedBAwPC.xml': '\\textsc{pc}v2',
                 'examples/ABP.xml': '\\textsc{abp}',
                 'examples/BRP.xml': '\\textsc{brp}',
                 'examples/ABP_F.xml': '\\textsc{abp}$_f$',
                 'examples/BRP_F.xml': '\\textsc{brp}$_f$',
                 'examples/SlidingWindow.xml': '\\textsc{sw}$_f$',
                 'examples/Synchronous.xml': '\\textsc{sync}$_f$',
                 'examples/Jingle.xml': '\\textsc{Jingle}$_f$'
                 }
    sem_dict = {'lossy': '\\textsc{lcs}',
                'stuttering': '\\textsc{slcs}',
                'multiset': 'M-set'
                }
    
    header = ('{\\bf P} & {\\bf Sem} & {\\bf Gen. Time} & {\\bf SMT} ' +
        '& {\\bf Aut.} & {\\bf Alt.} & {\\bf Res} \\\\ \n')

    f = settings['file']

    name = name_dict[f]
    semantics = sem_dict[settings['semantics']]
    constraint_generation = round(engine.get_constraint_generation_time(), 1)
    smt_time = round(engine.get_smt_time(), 1)
    states = engine.cs.constraint_gen.b_total_number_of_states
    trans = engine.cs.constraint_gen.b_total_number_of_trans
    automaton = str(states) + '/' + str(trans)
    alternations = settings['bound'] * 2
    res = result
    if res:
        res = 'U'
    else:
        res = 's'

#    total_time = round(elapsed, 1)
    table_entry = ' & '.join([str(a) for a in [name,
                                               semantics,
                                               constraint_generation,
                                               smt_time,
                                               automaton,
                                               alternations,
                                               res
                                               ]]) + ' \\\\ \n'

    out = open(settings['res_file'], 'a')
    out.write(header)
    out.write(table_entry)
    out.close()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Prototype verifier based' +
                                     ' on mode-alternation bounding.')
    parser.add_argument('--file', type=str,
                        help='an xml file containing the protocol to verify')
    parser.add_argument('--settings', type=str, default='SETTINGS',
                        help='a text file with all settings')
    parser.add_argument('--query', type=str, help='the type of query to use')
    parser.add_argument('--semantics', type=str, choices=['lossy', 'multiset', 'stuttering'],
                        help='Defines channel semantics. Overrides settings file.')
    parser.add_argument('--bound', type=int, default=0,
                        help='Bound on the number of phases. The total number of will be 2*BOUND')
    parser.add_argument('--bad', type=str, help='Name of bad state to reach')
    parser.add_argument('--role', type=str, help='Name of role in which to reach the bad state')
    parser.add_argument('--prefix_channels', default=False,
                        dest='prefix_channels', action='store_true',
                        help='If set, infers channels from the prefixes of messages')  
    args = parser.parse_args()
    arg_dict = vars(args)

    start = time.time()
    engine = mab.engine.Engine(args.settings, arg_dict)
    settings = engine.settings
    res = engine.has_solution()
    elapsed = (time.time() - start)
    
    if res:
        print 'Uh-oh. Some bad state found within the bound ' + str(settings['bound']*2)
#        if settings['export_counter_ex']:
#            engine.export_counter_example('counter_ex_')

    else:
        print 'No bad state reachable with bound ' + str(settings['bound']*2)

    print 'Total processing took ' + str(elapsed) + ' seconds'
    print 'Constraint generation needed ' + str(engine.get_constraint_generation_time()) + ' seconds'
    print 'SMT solver needed ' + str(engine.get_smt_time()) + ' seconds'
    print_table(elapsed, engine, settings, res)
    print 'Done and done.'