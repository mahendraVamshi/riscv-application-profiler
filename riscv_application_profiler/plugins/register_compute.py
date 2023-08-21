from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import statistics

def register_compute(master_inst_list: list):
    '''
    Computes the number of reads and writes to each register.
    Args:
        - master_inst_list: A list of InstructionEntry objects.

    Returns:
        - A list of registers and a dictionary with the registers as keys and the number of reads
    '''
    logger.info("computing register read writes.")
    reg_list=list(consts.reg_file.keys())
    regs={i:{'write_count':0, 'read_count':0} for i in reg_list}
    ret_dict = {'Register': [], 'Reads': [], 'Writes': []}

    for entry in master_inst_list:
        if (entry.rs1 is not None):
            name = str(entry.rs1[1]) + str(entry.rs1[0])
            regs[name]['read_count'] += 1
        if (entry.rs2 is not None):
            name = str(entry.rs2[1]) + str(entry.rs2[0])
            regs[name]['read_count'] += 1
        if (entry.rd is not None):
            name = str(entry.rd[1]) + str(entry.rd[0])
            # if (entry.reg_commit is not None):         
            #     name1 = str(entry.reg_commit[0]) + str(entry.reg_commit[1])
            #     if (name != name1):
            #         print(entry)
            regs[name]['write_count'] += 1
            if (entry.reg_commit is None):
                if 'fence' in entry.instr_name or 'j' in entry.instr_name:
                    continue
                # print(entry)
    
    for reg in reg_list:
        ret_dict['Register'].append(reg)
        ret_dict['Reads'].append(regs[reg]['read_count'])
        ret_dict['Writes'].append(regs[reg]['write_count'])
    return(ret_dict)

def fregister_compute(master_inst_list: list,extension_list: list):
    '''
    Computes the number of reads and writes to each floating point register.

    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - extension_list: A list of extensions.

    Returns:
        - A list of registers and a dictionary with the registers as keys and the number of reads
        
    '''
    reg_list=[]
    regs={}
    if 'F' not in extension_list or 'D' not in extension_list:
        return(reg_list, regs)
    logger.info("computing register read writes.")
    reg_list=list(consts.freg_file.keys())
    regs={i:{'write_count':0, 'read_count':0} for i in reg_list}
    ret_dict = {'F_Register': [], 'Reads': [], 'Writes': []}

    for entry in master_inst_list:
        inst_name=str(entry.instr_name)
        if 'f' in inst_name:
            if (entry.rs1 is not None and 'x' not in entry.rs1[1]):
                name = str(entry.rs1[1]) + str(entry.rs1[0])
                regs[name]['read_count'] += 1
            if (entry.rs2 is not None and 'x' not in entry.rs2[1]):
                name = str(entry.rs2[1]) + str(entry.rs2[0])
                regs[name]['read_count'] += 1
            if (entry.rd is not None and 'x' not in entry.rd[1]):
                name = str(entry.rd[1]) + str(entry.rd[0])
                regs[name]['write_count'] += 1

    for reg in reg_list:
        ret_dict['F_Register'].append(reg)
        ret_dict['Reads'].append(regs[reg]['read_count'])
        ret_dict['Writes'].append(regs[reg]['write_count'])
    return(ret_dict)