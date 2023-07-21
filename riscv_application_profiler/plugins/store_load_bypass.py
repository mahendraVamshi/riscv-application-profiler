from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts

def store_load_bypass (master_inst_list: list, load_list, store_list):

    logger.info("computing store load bypass.")
    store_address_list=[]
    load_address_list=[]
    bypass_dict={}
    for i in master_inst_list:
        if (i.reg_commit is not None):
            consts.reg_file[f'x{i.reg_commit[1]}'] = i.reg_commit[2]
        if (i in load_list or i in store_list):
            if ('c.sp' in i.instr_name):
                base = int(consts.reg_file['x2'],16)
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

                
