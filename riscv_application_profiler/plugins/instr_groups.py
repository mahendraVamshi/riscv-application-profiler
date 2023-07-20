# See LICENSE for licensing information.

# this file is a plugin for riscv_application_profiler
# this file classifies instructions into groups based on the conditions defined by the user.

from riscv_isac.log import *
from riscv_application_profiler.consts import *
import re

def group_by_operation(operations: list, isa, extension_list, master_inst_list: list):
    

    #print (*master_inst_list[:6])
    '''
    Groups instructions based on the operation.

    Args:
        - operations: A list of operations to group by.
        - master_inst_list: A list of InstructionEntry objects.

    Returns:
        - A tuple containing a dictionary with the operations as keys and a list of
            InstructionEntry objects as values, and a dictionary with the operations as
            keys and the number of instructions in each group as values.
    '''
    logger.info("Grouping instructions by operation.")
    
    # Create a dictionary with the operations as keys

    op_dict = {f'{op}': [] for op in operations}

    for extension in extension_list:
        for op in operations:
            for entry in master_inst_list:
                try:
                    if entry.instr_name in ops_dict[isa][extension][op]:
                        op_dict[op].append(entry)
                except KeyError as e:
                    logger.error(f'Extension {e} not supported.')
                    exit(1)

    counts = {f'{op}': len(op_dict[op]) for op in operations}
    logger.debug('Done.')
    return (op_dict, counts)







def privilege_modes(log):
    logger.info("Computing privilege modes.")
    mode_dict = {'user': [], 'supervised': [], 'reserved': [], 'machine': []}
    privilege_mode_regex = r'^core\s+\d+:\s+(\d+)'
    with open(log, 'r') as log_file:
        for line in log_file:
            match = re.match(privilege_mode_regex, line)
            if match is not None:
                x = int(match.group(1))
                if x is not None:
                    if x==0:
                        mode_dict['user'].append(line)
                    elif x==1:
                        mode_dict['supervised'].append(line)
                    elif x==2:
                        mode_dict['reserved'].append(line)
                    elif x==3:
                        mode_dict['machine'].append(line)
    #print(len(op_dict['3']))
    counts = {op: len(mode_dict[op]) for op in mode_dict.keys()}
    return (mode_dict, counts)