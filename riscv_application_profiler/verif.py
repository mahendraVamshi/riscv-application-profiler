import importlib
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
from riscv_application_profiler.utils import Utilities
import re
import os

def verify(check):
    count = 0
    # utils = Utilities(check)
    # utils.metadata()
    with open(check, 'r+') as check_file:
        
        # Iterate through each line in the log file.
        for line in check_file:
            match = re.match('\[\s+(\d+)\]', line)
            if match is not None:
                # Extract the privilege mode value from the regex match.
                x = int(match.group(1))
                if x is not None:
                    count += x

    print('Actual number of cycles: ')
    print(count//10)

def modi(check, mast_dict):
    with open(check, 'r') as check_file, open("mine.txt", 'w') as mine:
        l = list(mast_dict.values())
        l1 = list(mast_dict.keys())
        for idx,line in enumerate(check_file):
            line = line.strip()
            entry = l1[idx]
            n_line = line+ '\t'+ '--------    ' + entry.instr_name + '\t'+ '['+str(l[idx])+']'
            mine.writelines(n_line+'\n')