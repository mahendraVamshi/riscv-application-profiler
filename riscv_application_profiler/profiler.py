import re
from riscv_application_profiler.consts import *
import pprint as prettyprint
import math

def run(log, output):
    pass

def old(log, disass, output):
    '''
    Parses the given log and generates meaningful information.
    '''
    
    # Open the log file and read lines
    with open(log, 'r') as logfile:
        # Read the log file
        lines = logfile.readlines()

    # Find all the matches
    cl_matches_list=[]
    for line in lines :
        matches=re.findall(commitlog_regex,line)
        cl_matches_list=cl_matches_list+matches
    #cl_matches_list = [re.findall(commitlog_regex, line, re.M) for line in lines]

    #for i in range(20):
    #   print (cl_matches_list[2])

    # Open the disassembly file and read lines
    with open(disass, 'r') as disassfile:
        # Read the disassembly file
        lines = disassfile.readlines()

    # Find all the matches
    d_matches_list = [re.findall(disass_regex, line, re.M) for line in lines]

    #print(cl_matches_list[10000][0][1][2:])
    #new

    #print(len(cl_matches_list))

    load_count=0
    reg_write_count=0
    store_count=0
    branch_count=0
    jump_count=0
    R_type_count=0
    I_type_count=0
    U_type_count=0

    for i in range (10):#len(cl_matches_list)):

        instruction= "{0:08b}".format(int(cl_matches_list[i][1][2:], 16))
        
        if (len(instruction)!=32):
            d=(32-len(instruction))
            instruction=('0'*d)+instruction
        print(instruction[25:32])
        if (instruction[25:32]=='0000011'):
            load_count+=1
        elif(instruction[25:32]=='0100011'):
            store_count+=1
        elif(instruction[25:32]=='1100011'):
            branch_count+=1

        elif(instruction[25:32]=='1101111'):
            jump_count+=1
        elif(instruction[24:31]=='0010011'):
            I_type_count+=1
            

        #print(instsruction)


    
