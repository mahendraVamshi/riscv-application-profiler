from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import statistics
import os
import yaml

script_directory = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '..', 'config.yaml')
with open(config_path, 'r') as config_file:
    config = yaml.safe_load(config_file)

def register_compute(master_inst_list: list):
    '''
    Computes the number of reads and writes to each register.
    Args:
        - master_inst_list: A list of InstructionEntry objects.

    Returns:
        - A list of registers and a dictionary with the registers as keys and the number of reads
    '''
    if 'cfg1' in config['profiles']:
        metrics = config['profiles']['cfg1']['metrics']
        if 'register_compute' in metrics:
            logger.info("Computing register read writes.")
    
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
    if 'cfg1' in config['profiles']:
        metrics = config['profiles']['cfg1']['metrics']
        if 'register_compute' in metrics:
            logger.info("Computing register read writes.")
    
    reg_list=list(consts.freg_file.keys())
    regs={i:{'write_count':0, 'read_count':0} for i in reg_list}

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
    return(reg_list, regs)