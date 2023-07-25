from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts

def csr_compute(master_inst_list: list, ops_dict: dict):
    '''
    Computes the number of reads and writes to each CSR.
    
    Args:
        - master_inst_list: A list of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of
    
    Returns:
        - A list of CSRs and a dictionary with the CSRs as keys and the number of reads
            and writes to each CSR as values.
    '''
    
    csr={}
    csr_reg_list=[]
    logger.info("computing CSRs.")
    for entry in master_inst_list: 
        
        if entry in ops_dict['csrs']:
            if entry.csr is None:
                if 'f' in entry.instr_name:
                    if 'frcsr' in entry.instr_name or 'fscsr' in entry.instr_name:
                        csr_reg='fcsr'
                    if 'frrm' in entry.instr_name or 'fsrm' in entry.instr_name:
                        csr_reg='frm'
                    if 'frflags' in entry.instr_name or 'fsflags' in entry.instr_name:
                        csr_reg='fflags'
                    
                    if csr_reg in csr:
                        if 'fr' in entry.instr_name:
                            csr[csr_reg]['read']+=1
                        elif 'fs' in entry.instr_name:
                            csr[csr_reg]['write']+=1
                        
                    else:
                        if 'fr' in entry.instr_name:
                            csr[csr_reg]={'read':1,'write':0}
                            csr_reg_list.append(csr_reg)
                        elif 'fs' in entry.instr_name:
                            csr[csr_reg]={'read':0,'write':1}
                            csr_reg_list.append(csr_reg)
                # else:
                #     print(entry)
                
            else:
                csr_hex=str(hex(entry.csr))
                csr_reg=consts.csr_file[csr_hex]
                if csr_reg in csr:
                    if 'rw' in entry.instr_name:
                        rd=str(entry.rd[1])+str(entry.rd[0])
                        if rd == 'x0':
                            csr[csr_reg]['write']+=1
                        else:
                            csr[csr_reg]['read']+=1
                            csr[csr_reg]['write']+=1
                    elif 'rs' in entry.instr_name or 'rc' in entry.instr_name:
                        rs1=str(entry.rs1[1])+str(entry.rs1[0])
                        if rs1 == 'x0':
                            csr[csr_reg]['read']+=1
                        else:
                            csr[csr_reg]['read']+=1
                            csr[csr_reg]['write']+=1
                else:
                    
                    if 'rw' in entry.instr_name:
                        rd=str(entry.rd[1])+str(entry.rd[0])
                        if rd == 'x0':
                            csr[csr_reg]={'read':0,'write':1}
                            csr_reg_list.append(csr_reg)
                        else:
                            csr[csr_reg]={'read':1, 'write':1}
                            csr_reg_list.append(csr_reg)
                    elif 'rs' in entry.instr_name or 'rc' in entry.instr_name:
                        rs1=str(entry.rs1[1])+str(entry.rs1[0])
                        if rs1 == 'x0':
                            csr[csr_reg]={'read':1,'write':0}
                            csr_reg_list.append(csr_reg)
                        else:
                            csr[csr_reg]={'read':1, 'write':1}
                            csr_reg_list.append(csr_reg)
    return(csr_reg_list, csr)

