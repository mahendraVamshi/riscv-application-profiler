# See LICENSE for licensing information.

# this file is a plugin for riscv_application_profiler
# this file classifies instructions into groups based on the conditions defined by the user.

from riscv_isac.log import *
from riscv_application_profiler.consts import *
import re
import os
import yaml

script_directory = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '..', 'config.yaml')
with open(config_path, 'r') as config_file:
    config = yaml.safe_load(config_file)



def group_by_operation(operations: list, isa, extension_list, master_inst_list: list):
    

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
    if 'cfg1' in config['profiles']:
        metrics = config['profiles']['cfg1']['metrics']
        if 'instr_groups' in metrics:
            logger.info("Grouping instructions by operation.")
    
    # Create a dictionary with the operations as keys

    op_dict = {f'{op}': [] for op in operations}
    ops_count={f'{op}': {'counts':0} for op in operations}
    op_list = [f'{op}' for op in operations]
    extension_instruction_list = []

    for entry in master_inst_list:
        for extension in extension_list:
            for op in operations:
                try:
                    if entry.instr_name in ops_dict[isa][extension][op]:
                        op_dict[op].append(entry)
                        ops_count[op]['counts']+=1
                        extension_instruction_list.append(entry)
                except KeyError as e:
                    logger.error(f'Extension {e} not supported.')
                    exit(1)
    counts = {f'{op}': len(op_dict[op]) for op in operations}
    logger.debug('Done.')
    return (op_list,ops_count,extension_instruction_list,op_dict)


def privilege_modes(log):
    '''
    Computes the privilege modes.
    
    Args:
        - log: The path to the log file.
        
    Returns:
        - A list of privilege modes.
        - A dictionary with the privilege modes as keys and the number of instructions in each group as values.
    '''
    if 'cfg1' in config['profiles']:
        metrics = config['profiles']['cfg1']['metrics']
        if 'instr_groups' in metrics:
            logger.info("Computing privilege modes.")
    
    mode_list = ['user', 'supervised', 'machine']
    mode_dict = {'user': {'count':0}, 'supervised': {'count':0}, 'machine': {'count':0}}
    user_list = []
    supervised_list = []
    reserved_list = []
    machine_list = []
    with open(log, 'r') as log_file:
        for line in log_file:
            match = re.match(privilege_mode_regex, line)
            if match is not None:
                x = int(match.group(1))
                if x is not None:
                    if x==0:
                        mode_dict['user']['count']+=1
                        user_list.append(line)
                    elif x==1:
                        mode_dict['supervised']['count']+=1
                        supervised_list.append(line)
                    elif x==3:
                        mode_dict['machine']['count']+=1
                        machine_list.append(line)

    return (mode_list,mode_dict)