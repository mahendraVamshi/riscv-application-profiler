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
    
    # Initialize dictionaries and lists
    csr = {}
    csr_reg_list = []
    ret_dict = {'CSR': [], 'Reads': [], 'Writes': []}

    # Logging the CSR computation process
    logger.info("Computing CSRs.")

    # Loop through CSR instructions
    for entry in ops_dict['csrs']:
        # If no CSR value is specified
        if entry.csr is None:
            if 'f' in entry.instr_name:
                csr_reg = entry.instr_name[0] + entry.instr_name[2:]
                
                if csr_reg not in csr_reg_list:
                    # Create a new entry for the CSR
                    csr_reg_list.append(csr_reg)
                    csr[csr_reg] = {'read': 0, 'write': 0}
                
                # Update read/write counts for the corresponding CSR
                if 'fr' in entry.instr_name:
                    csr[csr_reg]['read'] += 1
                elif 'fs' in entry.instr_name:
                    csr[csr_reg]['write'] += 1
        # If a CSR value is specified
        else:
            csr_hex = str(hex(entry.csr))
            csr_reg = consts.csr_file.get(csr_hex)
            
            if csr_reg is not None and csr_reg not in csr_reg_list:
                # Create a new entry for the CSR
                csr_reg_list.append(csr_reg)
                csr[csr_reg] = {'read': 0, 'write': 0}
            
            if csr_reg is not None:
                # Update read/write counts for the corresponding CSR
                if 'rw' in entry.instr_name:
                    rd = str(entry.rd[1]) + str(entry.rd[0])
                    if rd == 'x0':
                        csr[csr_reg]['write'] += 1
                    else:
                        csr[csr_reg]['read'] += 1
                        csr[csr_reg]['write'] += 1
                elif 'rs' in entry.instr_name or 'rc' in entry.instr_name:
                    rs1 = str(entry.rs1[1]) + str(entry.rs1[0])
                    if rs1 == 'x0':
                        csr[csr_reg]['read'] += 1
                    else:
                        csr[csr_reg]['read'] += 1
                        csr[csr_reg]['write'] += 1

    # Populate the ret_dict with CSR information
    for entry in csr_reg_list:
        ret_dict['CSR'].append(entry)
        ret_dict['Reads'].append(csr[entry]['read'])
        ret_dict['Writes'].append(csr[entry]['write'])

    # Return the final results
    return ret_dict

