# See LICENSE for licensing information.

# this file is a plugin for riscv_application_profiler
# this file classifies instructions into groups based on the conditions defined by the user.

from riscv_isac.log import *
from riscv_application_profiler.consts import *
import re

def group_by_operation(operations: list, isa, master_inst_list: list):
    

    print (*master_inst_list[:6])
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

    isa=isa.lower()
    ISA=isa[:4]


    group = re.findall(isa_regex,isa)
    extensions_list=[i for i in group[0] if i!='']
    print(extensions_list)
    

    # Create a dictionary with the operations as keys
    op_dict = {f'{op}': [] for op in operations}
    for op in operations:
        print(op)
        for entry in master_inst_list:
            if entry.instr_name is None:
                continue
            #if entry.instr_name in ops_dict[op][isa]:

            for i in extensions_list:

                if entry.instr_name in ops_dict[ISA][i][op]:
                    op_dict[op].append(entry)
    counts = {f'{op}': len(op_dict[op]) for op in operations}
    logger.info('Done.')
    return (op_dict, counts)
