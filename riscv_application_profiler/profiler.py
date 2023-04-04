import re
from riscv_application_profiler.consts import *
import pprint as prettyprint
import math
from riscv_isac.data.rvopcodesdecoder import disassembler
from riscv_isac.log import *
from riscv_isac.plugins.spike import *
from riscv_application_profiler.plugins import instr_groups
from riscv_application_profiler.plugins import branch_ops

def run(log, output, verbose):
    logger.debug("Entered run().")
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
    isac_decoder.setup(arch='rv64', opcodes_path=f'{output}/riscv-opcodes')
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
        'branches'
    ]
    op_dict1, counts1 = instr_groups.group_by_operation(groups, master_inst_list)

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