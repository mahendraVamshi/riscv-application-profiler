import re
from riscv_application_profiler.consts import *
import pprint as prettyprint

def run(log, disass, output):
    '''
    Parses the given log and generates meaningful information.
    '''
    
    # Open the log file and read lines
    with open(log, 'r') as logfile:
        # Read the log file
        lines = logfile.readlines()

    # Find all the matches
    cl_matches_list = [re.findall(commitlog_regex, line, re.M) for line in lines]

    # Open the disassembly file and read lines
    with open(disass, 'r') as disassfile:
        # Read the disassembly file
        lines = disassfile.readlines()

    # Find all the matches
    d_matches_list = [re.findall(disass_regex, line, re.M) for line in lines]
