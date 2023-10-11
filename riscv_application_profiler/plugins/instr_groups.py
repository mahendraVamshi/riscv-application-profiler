# See LICENSE for licensing information.

# this file is a plugin for riscv_application_profiler
# this file classifies instructions into groups based on the conditions defined by the user.

from riscv_isac.log import *
from riscv_application_profiler.consts import *
import re

def group_by_operation(operations: list, isa, extension_list, master_inst_list: list, config, cycle_accurate_config):
    

    '''
    Groups instructions based on the operation.

    Args:
        - operations: A list of operations to group by.
        - master_inst_list: A list of InstructionEntry objects.

    Returns:
        - A list of operations.
        - A dictionary with the operations as keys and the number of instructions in each group as values.
        - A list of InstructionEntry objects based on input extensions.
        - A dictionary with the operations as keys and a list of InstructionEntry objects as values.

    '''
    # Log the start of the process for grouping instructions by operation.
    logger.info("Grouping instructions by operation.")

    # Create a dictionary to hold instructions grouped by operation.
    op_dict = {f'{op}': {} for op in operations}

    # Create a dictionary to keep track of instruction counts per operation.
    ops_count = {f'{op}': {'counts': 0} for op in operations}

    # Create a dictionary to hold the resulting counts and operation names.
    ret_dict = {'Operation': [f'{op}' for op in operations], 'Counts': []}

    # Initialize a list to store extension-related instructions.
    extension_instruction_list = []

    # Iterate through the list of instructions in master_inst_list.
    for entry in master_inst_list:
        for extension in extension_list:
            for op in operations:
                try:
                        # Check if the current instruction belongs to the specified operation.
                    if entry.instr_name in ops_dict[isa][extension][op]:
                        # Append the instruction to the corresponding operation group.
                        if cycle_accurate_config != None:
                            for inst in cycle_accurate_config['cycles']['instructions_cycles']:
                                if re.match(inst, entry.instr_name) != None:                              
                                    op_dict[op][entry] = cycle_accurate_config['cycles']['instructions_cycles'][inst]
                                    master_inst_list[entry] = cycle_accurate_config['cycles']['instructions_cycles'][inst]
                                else:
                                    # print(entry.instr_name)
                                    op_dict[op][entry] = 1
                        else:
                            op_dict[op][entry]=1
                        
                        # Increment the instruction count for the operation.
                        ops_count[op]['counts'] += 1
                        
                        # Append the instruction to the extension instruction list.
                        extension_instruction_list.append(entry)
                except KeyError as e:
                    # Handle the case where the extension is not supported.
                    logger.error(f'Extension {e} not supported.')
                    exit(1)

    # Populate the 'Counts' field in the ret_dict with the instruction counts per operation.
    ret_dict['Counts'] = [len(op_dict[op]) for op in operations]
    # op_dict['total_cycles'] = sum([op_dict[op][entry] for op in operations for entry in op_dict[op]])
    # print(op_dict['total_cycles'])

    # Log the completion of the computation.
    logger.info("Done")

    # Return the resulting dictionaries containing grouped instructions and counts.
    return (ret_dict,extension_instruction_list,op_dict)


def privilege_modes(log,config):
    '''
    Computes the privilege modes.
    
    Args:
        - log: The path to the log file.
        
    Returns:
        - A list of privilege modes.
        - A dictionary with the privilege modes as keys and the number of instructions in each group as values.
    '''
    # Log the start of the process for computing privilege modes.
    logger.info("Computing privilege modes.")
    privilege_mode_regex = config['profiles']['cfg']['privilege_mode_regex']

    # List of privilege modes to track: user, supervised, and machine.
    mode_list = ['user', 'supervised', 'machine']

    # Initialize a dictionary to track the counts of privilege modes.
    mode_dict = {'user': {'count': 0}, 'supervised': {'count': 0}, 'machine': {'count': 0}}

    # Initialize a dictionary to hold the resulting counts and privilege mode names.
    ret_dict = {'Privilege Mode': mode_list, 'Counts': []}

    # Open the specified log file for reading.
    with open(log, 'r') as log_file:
        # Iterate through each line in the log file.
        for line in log_file:
            # Attempt to match the line against the privilege mode regex pattern.
            match = re.match(privilege_mode_regex, line)
            if match is not None:
                # Extract the privilege mode value from the regex match.
                x = int(match.group(1))
                if x is not None:
                    # Update the counts for each privilege mode based on the extracted value.
                    if x == 0:
                        mode_dict['user']['count'] += 1
                    elif x == 1:
                        mode_dict['supervised']['count'] += 1
                    elif x == 3:
                        mode_dict['machine']['count'] += 1

    # Populate the 'Counts' field in the ret_dict with the privilege mode counts.
    ret_dict['Counts'] = [mode_dict[mode]['count'] for mode in mode_list]

    # Log the completion of the privilege mode computation.
    logger.info('Done.')

    # Return the resulting dictionary containing privilege mode counts.
    return ret_dict