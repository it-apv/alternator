#! /Library/Frameworks/Python.framework/Versions/2.7/bin/python

'''
Created on Aug 3, 2012

@author: jonathan
'''
import argparse
import mab.engine
import time

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Prototype verifier based' +
                                     ' on mode-alternation bounding.')
    parser.add_argument('--file', type=str,
                        help='an xml file containing the protocol to verify')
    parser.add_argument('--settings', type=str, default='SETTINGS',
                        help='a text file with all settings')
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
    
    if engine.has_solution():
        elapsed = (time.time() - start)
        print 'Uh-oh. Some bad state found within the bound ' + str(settings['bound'])
        if settings['export_counter_ex']:
            engine.export_counter_example('counter_ex_')

    else:
        elapsed = (time.time() - start)
        print 'No bad state reachable with bound ' + str(settings['bound'])
    print 'Total processing took ' + str(elapsed) + ' seconds'
    print 'SMT solver needed ' + str(engine.get_smt_time()) + ' seconds'
