import re
from riscv_application_profiler.consts import *
import pprint as prettyprint

def run(log, output):
    '''
    Parses the given log and generates meaningful information.
    '''
    
    # Open the log file and read lines
    with open(log, 'r') as logfile:
        # Read the log file
        lines = logfile.readlines()

    # Find all the matches
    matches_list = [re.findall(commitlog_regex, line, re.M) for line in lines]

    # log the number of matches
    print(f"Found {len(matches_list)} matches out of {len(lines)} lines.")
