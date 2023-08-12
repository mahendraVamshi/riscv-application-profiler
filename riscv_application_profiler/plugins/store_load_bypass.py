from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
import os
import yaml

script_directory = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '..', 'config.yaml')
with open(config_path, 'r') as config_file:
    config = yaml.safe_load(config_file)


def store_load_bypass (master_inst_list: list, ops_dict: dict):
    '''
    Computes the number of instances of store load bypass.
    
    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of
            InstructionEntry objects as values.
    
    Returns:
        - A list of addresses and a dictionary with the addresses as keys and the number of instances of store load bypass as values.
        
    '''
    if 'cfg1' in config['profiles']:
        metrics = config['profiles']['cfg1']['metrics']
        if 'store_load_bypass' in metrics:
            logger.info("Computing store load bypass.")
    
    load_list=ops_dict['loads']
    store_list=ops_dict['stores']
    store_address_list=[]
    load_address_list=[]
    bypass_dict={}
    for i in master_inst_list:
        if (i.reg_commit is not None):
            consts.reg_file[f'x{i.reg_commit[1]}'] = i.reg_commit[2]
        if (i in load_list or i in store_list):
            if ('sp' in i.instr_name):
                base = int(consts.reg_file['x2'],16)
                if (i.imm is None):
                    address = hex(base)
                else:
                    address = hex(base+i.imm)
            else:
                base = int(consts.reg_file[f'x{i.rs1[0]}'],16)
                if (i.imm is None):
                    address = hex(base)
                else:
                    address = hex(base+i.imm)
        if (i in store_list):
            store_address_list.append(address)
        elif (i in load_list):
            if address in store_address_list:
                if address in load_address_list:
                    bypass_dict[address]['counts']+=1
                else:
                    load_address_list.append(address)
                    bypass_dict[address]={'counts':0}
    return(load_address_list,bypass_dict)

                
