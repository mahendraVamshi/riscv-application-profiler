from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import statistics

def raw_compute(master_inst_list: list):
    '''
    Groups instructions based on the branch offset.

    Args:
        - master_inst_list: A list of InstructionEntry objects.

    Returns:
        - A tuple containing a dictionary with the operations as keys and a list of
            InstructionEntry objects as values, and a dictionary with the operations as
            keys and the number of instructions in each group as values.
    '''
    # Initialize the process of computing register reads after writes.
    logger.info("Computing register reads after writes.")

    # Get a list of all registers in the register file.
    reg_list = list(consts.reg_file.keys())

    # Initialize a dictionary to hold register information, initially all with a depth of 1.
    regs = {i: {'depth': 1} for i in reg_list}

    # Initialize dictionaries to store results and raw data.
    ret_dict = {'Instructions': [], 'Depth': [], 'Count': []}
    raw = {}

    # Initialize a list to store combined instructions.
    instruction_list = []

    # Initialize a list to store names of previously encountered registers.
    prev_names = []

    # Iterate through the list of instructions in master_inst_list.
    for entry in master_inst_list:
        # Check if the instruction uses rs1 register.
        if entry.rs1 is not None:
            name = str(entry.rs1[1]) + str(entry.rs1[0])
            instr = str(entry.instr_name)
            
            # Check if this register name was encountered before.
            if name in prev_names:
                instruction = prev_instr + '  ' + instr
                
                # Check if the combined instruction is in raw data.
                if instruction in raw:
                    # Check if the register depth matches raw depth.
                    if regs[name]['depth'] == raw[instruction]['depth']:
                        raw[instruction]['count'] += 1
                        prev_names.remove(name)
                        regs[name]['depth'] = 1
                else:
                    raw[instruction] = {'depth': regs[name]['depth'], 'count': 1}
                    instruction_list.append(instruction)
                    prev_names.remove(name)
                    regs[name]['depth'] = 1
            else:
                regs[name]['depth'] += 1
        
        # Check if the instruction uses rs2 register.
        if entry.rs2 is not None:
            name = str(entry.rs2[1]) + str(entry.rs2[0])
            instr = str(entry.instr_name)
            
            # Check if this register name was encountered before.
            if name in prev_names:
                instruction = prev_instr + '  ' + instr
                
                # Check if the combined instruction is in raw data.
                if instruction in raw:
                    # Check if the register depth matches raw depth.
                    if regs[name]['depth'] == raw[instruction]['depth']:
                        raw[instruction]['count'] += 1
                        prev_names.remove(name)
                        regs[name]['depth'] = 1
                else:
                    raw[instruction] = {'depth': regs[name]['depth'], 'count': 1}
                    instruction_list.append(instruction)
                    prev_names.remove(name)
                    regs[name]['depth'] = 1
            else:
                regs[name]['depth'] += 1
        
        # Check if the instruction defines a destination register (rd).
        if entry.rd is not None:
            name = str(entry.rd[1]) + str(entry.rd[0])
            prev_instr = str(entry.instr_name)
            
            # Check if this register name was encountered before.
            if name not in prev_names:
                prev_names.append(name)
            else:
                regs[name]['depth'] = 1

    # Populate the result dictionary from raw data.
    for entry in raw:
        ret_dict['Instructions'].append(entry)
        ret_dict['Count'].append(raw[entry]['count'])
        ret_dict['Depth'].append(raw[entry]['depth'])

    # Log the completion of the computation.
    logger.info("Done")

    # Return the result dictionary.
    return ret_dict
