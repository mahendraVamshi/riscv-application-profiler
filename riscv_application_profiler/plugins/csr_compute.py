from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts

def csr_compute(master_inst_list: list, ops_dict: dict):
    
    csr={}
    csr_reg_list=[]
    logger.info("computing CSRs.")
    for entry in master_inst_list: 
        
        if entry.instr_name in ops_dict['csrs']:
            if entry.csr is None:
                continue
            csr_hex=str(hex(entry.csr))
            csr_reg=consts.csr_file[csr_hex]
            if csr_reg in csr:
                csr[csr_reg]['count'] += 1
            else:
                csr[csr_reg]={'count':1}
                csr_reg_list.append(csr_reg)

    return(csr_reg_list, csr)

