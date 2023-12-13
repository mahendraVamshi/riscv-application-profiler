from riscv_isac.log import *
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts

def csr_compute(master_inst_dict: dict, ops_dict: dict, extension_used: list, config, cycle_accurate_config):
    '''
    Computes the number of reads and writes to each CSR.
    
    Args:
        - master_inst_dict: A dictionary of InstructionEntry objects.
        - ops_dict: A dictionary containing the operations as keys and a list of InstructionEntry objects as values.
        - extension_used: A list of extensions used in the application.
        - config: A yaml with the configuration information.
        - cycle_accurate_config: A dyaml with the cycle accurate configuration information.
    
    Returns:
        - A dictionary with the CSR names as keys and a list of reads and writes as values.
    '''
    
    # Initialize dictionaries and lists
    csr = {}
    csr_reg_list = []
    ret_dict = {'CSR': [], 'Reads': [], 'Writes': []}
    prev_inst_csr = None

    # Logging the CSR computation process
    logger.info("Computing CSRs.")
    for entry in master_inst_dict:
    # Loop through CSR instructions
        if entry in ops_dict['csrs']:
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
                        #for flushing pipe checking if write is happening to CSR register
                        prev_inst_csr = csr[csr_reg]
            # If a CSR value is specified
            else:
                csr_hex = hex(entry.csr)
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
                            prev_inst_csr = csr[csr_reg]
                        else:
                            csr[csr_reg]['read'] += 1
                            csr[csr_reg]['write'] += 1
                            prev_inst_csr = csr[csr_reg]
                    elif 'rs' in entry.instr_name or 'rc' in entry.instr_name:
                        if entry.rs1 is not None:
                            rs1 = str(entry.rs1[1]) + str(entry.rs1[0])
                        else:
                            rs1 = None
                        if entry.imm == 0 or rs1 == 'x0':
                            csr[csr_reg]['read'] += 1
                        else:
                            csr[csr_reg]['read'] += 1
                            csr[csr_reg]['write'] += 1
                            prev_inst_csr = csr[csr_reg]
        elif cycle_accurate_config != None:
            # if there's a writing to a csr instr, then we have to flush the pipe
            # so we have to add those flush instr to the next instruction 
            if prev_inst_csr != None:
                for op in ops_dict.keys():
                    if entry in ops_dict[op]:
                        ops_dict[op][entry] = ops_dict[op][entry] + cycle_accurate_config['cycles']['flush_cycles']['csr']
                        master_inst_dict[entry] = ops_dict[op][entry]
                        prev_inst_csr = None
    # Populate the ret_dict with CSR information
    for entry in csr_reg_list:
        ret_dict['CSR'].append(entry)
        ret_dict['Reads'].append(csr[entry]['read'])
        ret_dict['Writes'].append(csr[entry]['write'])

    logger.info("Done.")

    # Return the final results
    return ret_dict

