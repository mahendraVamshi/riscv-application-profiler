import re
from riscv_application_profiler.consts import *
import pprint as prettyprint
import math

def run(log, output):
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
    
    #d_matches_list = [re.findall(disass_regex, line, re.M) for line in lines]

    B_type_count=0



    for i in range (len(cl_matches_list)):
        
        # converting instruction which is hexadecimal format to binary 
        instruction= "{0:08b}".format(int(cl_matches_list[i][1][2:], 16))
        
        # making all instructions 32 bit wide by adding zeros in the start
        if (len(instruction)!=32):
            d=(32-len(instruction))
            instruction=('0'*d)+instruction

        #checking MSB value by shifting the number 31 bits to the right and AND with 1
        MSB = (int(instruction) >> 31) & 1

        #checking if the instruction is a branch
        if(instruction[25:32]=='1100011'):
            B_type_count+=1

            #the branch is positive if MSB is 0, else it is negative
            if MSB == 0:
                print("forward branch")
                print("instruction:",instruction)
                
                #calculating the offset size
                bits_11to8=instruction[20:24] #python indexing starts from left
                bits_8to11=bits_11to8[::-1] #reversing the order to concatenate for 12 bit immediate value

                bits_30to25=instruction[1:7]
                bits_25to30=bits_30to25[::-1]

                bit_7=instruction[24:25]

                offset=bit_7 + bits_25to30 + bits_8to11
                offset_int=int(offset,2)
                print("branch offset size is:",offset_int)

            else:
                print("backward branch")
                print("instruction: ",instruction)
                
                #calculating the offset size
                bits_11to8=instruction[20:24] #python indexing starts from left
                bits_8to11=bits_11to8[::-1] #reversing the order to concatenate for 12 bit immediate value

                bits_30to25=instruction[1:7]
                bits_25to30=bits_30to25[::-1]

                bit_7=instruction[24:25]
                bit_31= instruction[0:1]

                offset= bit_31+bit_7 + bits_25to30 + bits_8to11
                #offset= '11111111111111111111'+ offset
                offset_decimal=int(offset,2) #converting the string to integer
                offset_decimal = ~offset_decimal+1 #taking 2's complement
                print(offset_decimal)
               
               
                #print("branch offset size is:",offset_decimal)

                #calculating the loop iterations
                loop_iterations=0
                loop_iterations += abs (offset_decimal) // 2
                print("number of loop iterations is: ",loop_iterations)
                
    print("number of branches= %d" %(B_type_count))