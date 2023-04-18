import re
from riscv_application_profiler.consts import *
import pprint as prettyprint
import math
from riscv_isac.log import *
from riscv_isac.plugins.spike import *
from riscv_application_profiler.plugins import instr_groups
from riscv_application_profiler.plugins import branch_ops

def print_stats(op_dict, counts):
    '''
    Prints the statistics of the grouped instructions.

    Args:
        - op_dict: A dictionary with the operations as keys and a list of InstructionEntry
            objects as values.
        - counts: A dictionary with the operations as keys and the number of instructions
            in each group as values.
    '''
    logger.info("Printing statistics.")
    for op in op_dict.keys():
        logger.info(f'{op}: {counts[op]}')
    logger.info("Done.")

def run(log, isa, output, verbose):
    from build.rvopcodesdecoder import disassembler
    spike_parser = spike()
    spike_parser.setup(trace=str(log), arch='rv64')
    iter_commitlog = spike_parser.__iter__()
    with open(log, 'r') as logfile:
        # Read the log file
        lines = logfile.readlines()
        cl_matches_list = [iter_commitlog.__next__() for i in range(len(lines))]
    logger.info(f'Parsed {len(cl_matches_list)} instructions.')
    logger.info("Decoding...")
    isac_decoder = disassembler()
    isac_decoder.setup(arch='rv64')
    master_inst_list = []
    for entry in cl_matches_list:
        if entry.instr is None:
            continue
        temp_entry = isac_decoder.decode(entry)
        master_inst_list.append(temp_entry)

    logger.info("Done decoding instructions.")
    logger.info("Starting to profile...")

    # Grouping by operations
    groups = [
        'loads',
        'stores',
        'imm computes',
        'imm shifts',
        'reg computes',
        'reg shifts',
        'jumps',
        'branches',
        'mul'
    ]

   # groups = list(ops_dict.keys())

    op_dict1, counts1 = instr_groups.group_by_operation(groups, isa, master_inst_list)
    print_stats(op_dict1, counts1)

    # Group by branch sizes
    branch_threshold = 0
    op_dict2, counts2 = branch_ops.group_by_branch_offset(master_inst_list, branch_threshold)

    # Group by branch signs
    op_dict3, counts3 = branch_ops.group_by_branch_sign(master_inst_list)

# def old(log, disass, output):
#     '''
#     Parses the given log and generates meaningful information.
#     '''
    
#     # Open the log file and read lines
#     with open(log, 'r') as logfile:
#         # Read the log file
#         lines = logfile.readlines()

#     # Find all the matches
#     cl_matches_list=[]
#     for line in lines :
#         matches=re.findall(commitlog_regex,line)
#         cl_matches_list=cl_matches_list+matches
#     #cl_matches_list = [re.findall(commitlog_regex, line, re.M) for line in lines]

#     #for i in range(20):
#     #   print (cl_matches_list[2])

#     # Open the disassembly file and read lines
#     with open(disass, 'r') as disassfile:
#         # Read the disassembly file
#         lines = disassfile.readlines()

#     # Find all the matches
#     d_matches_list = [re.findall(disass_regex, line, re.M) for line in lines]

#     #print(cl_matches_list[10000][0][1][2:])
#     #new

#     #print(len(cl_matches_list))

#     load_count=0
#     reg_write_count=0
#     store_count=0
#     branch_count=0
#     jump_count=0
#     R_type_count=0
#     I_type_count=0
#     U_type_count=0

#     for i in range (10):#len(cl_matches_list)):

#         instruction= "{0:08b}".format(int(cl_matches_list[i][1][2:], 16))
        
#         if (len(instruction)!=32):
#             d=(32-len(instruction))
#             instruction=('0'*d)+instruction
#         print(instruction[25:32])
#         if (instruction[25:32]=='0000011'):
#             load_count+=1
#         elif(instruction[25:32]=='0100011'):
#             store_count+=1
#         elif(instruction[25:32]=='1100011'):
#             branch_count+=1

#         elif(instruction[25:32]=='1101111'):
#             jump_count+=1
#         elif(instruction[24:31]=='0010011'):
#             I_type_count+=1
            

#         #print(instsruction)

# from branch 'sowmya'
    # B_type_count=0



    # for i in range (len(cl_matches_list)):
        
    #     # converting instruction which is hexadecimal format to binary 
    #     instruction= "{0:08b}".format(int(cl_matches_list[i][1][2:], 16))
        
    #     # making all instructions 32 bit wide by adding zeros in the start
    #     if (len(instruction)!=32):
    #         d=(32-len(instruction))
    #         instruction=('0'*d)+instruction

    #     #checking MSB value by shifting the number 31 bits to the right and AND with 1
    #     MSB = (int(instruction) >> 31) & 1

    #     #checking if the instruction is a branch
    #     if(instruction[25:32]=='1100011'):
    #         B_type_count+=1

    #         #the branch is positive if MSB is 0, else it is negative
    #         if MSB == 0:
    #             print("forward branch")
                
                
    #             #calculating the offset size
    #             bits_11to8=instruction[20:24] #python indexing starts from left
    #             bits_8to11=bits_11to8[::-1] #reversing the order to concatenate for 12 bit immediate value

    #             bits_30to25=instruction[1:7]
    #             bits_25to30=bits_30to25[::-1]

    #             bit_7=instruction[24:25]

    #             offset=bit_7 + bits_25to30 + bits_8to11
    #             offset_positive=int(offset,2)
    #             print("branch offset size is: ",offset_positive)
    #             print("\n")

    #         else:
    #             print("backward branch")
                
                
    #             #calculating the offset size
    #             bits_11to8=instruction[20:24] #python indexing starts from left
    #             bits_8to11=bits_11to8[::-1] #reversing the order to concatenate for 12 bit immediate value

    #             bits_30to25=instruction[1:7]
    #             bits_25to30=bits_30to25[::-1]

    #             bit_7=instruction[24:25]
    #             bit_31= instruction[0:1]

    #             offset= bit_31+bit_7 + bits_25to30 + bits_8to11
                
    #             offset_decimal=int(offset,2) #converting the string to integer
    #             offset_negative = ~offset_decimal+1 #taking 2's complement
    #             print("branch offset size is: ",offset_negative)
                
               

    #             #calculating the loop iterations
    #             loop_iterations=0
    #             loop_iterations = abs (offset_negative) // 2
    #             print("number of loop iterations is: ",loop_iterations)
    #             print("\n")
                
    # print("number of branches= %d" %(B_type_count))