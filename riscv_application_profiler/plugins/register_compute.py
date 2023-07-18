from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import statistics

def register_compute(master_inst_list: list):
    '''
    Groups instructions based on the branch offset.

    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - branch_threshold: The threshold for a branch to be considered 'long'.

    Returns:
        - A tuple containing a dictionary with the operations as keys and a list of
            InstructionEntry objects as values, and a dictionary with the operations as
            keys and the number of instructions in each group as values.
    '''
    logger.info("computing register read writes.")
    reg_list=list(consts.reg_file.keys())
    regs={i:{'write_count':0, 'read_count':0} for i in reg_list}

    for entry in master_inst_list:
        if (entry.rs1 is not None):
            name = str(entry.rs1[1]) + str(entry.rs1[0])
            regs[name]['read_count'] += 1
        if (entry.rs2 is not None):
            name = str(entry.rs2[1]) + str(entry.rs2[0])
            regs[name]['read_count'] += 1
        if (entry.rd is not None):
            name = str(entry.rd[1]) + str(entry.rd[0])
            regs[name]['write_count'] += 1
    return(reg_list, regs)