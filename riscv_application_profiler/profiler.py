import importlib
from riscv_application_profiler.consts import *
import riscv_application_profiler.consts as consts
from riscv_isac.log import *
from riscv_isac.plugins.spike import *
from riscv_application_profiler.plugins import instr_groups
from riscv_application_profiler import verif
from riscv_application_profiler import plugins
import riscv_config.isa_validator as isaval
from riscv_application_profiler.utils import Utilities
import os
import yaml

# script_dir = os.path.dirname(os.path.abspath(__file__))
# config_path = os.path.join(script_dir, 'config.yaml')
# with open(consts.config_path, 'r') as config_file:
#     config = yaml.safe_load(config_file)

def print_stats(op_dict, counts):
    '''
    Prints the statistics of the grouped instructions.

    Args:
        - op_dict: A dictionary with the operations as keys and a list of InstructionEntry
            objects as values.
        - counts: A dictionary with the operations as keys and the number of instructions
            in each group as values.
    '''
    logger.info("Printing statistics.")
    for op in op_dict.keys():
        logger.info(f'{op}: {counts[op]}')
    logger.info("Done.")

def run(log, isa, output, verbose, config, cycle_accurate_config): #, check):
    from rvop_decoder.rvopcodesdecoder import disassembler
    spike_parser = spike()
    spike_parser.setup(trace=str(log), arch='rv64')
    iter_commitlog = spike_parser.__iter__()
    with open(log, 'r') as logfile:
        # Read the log file
        lines = logfile.readlines()
        cl_matches_list = [iter_commitlog.__next__() for i in range(len(lines))]
    isac_decoder = disassembler()
    isac_decoder.setup(arch='rv64')
    master_inst_list = []
    for entry in cl_matches_list:
        if entry.instr is None:
            continue
        temp_entry = isac_decoder.decode(entry)
        master_inst_list.append(temp_entry)
    master_inst_dict = {entry: 1 for entry in master_inst_list}
    logger.info(f'Parsed {len(master_inst_list)} instructions.')
    logger.info("Decoding...")
    logger.info("Done decoding instructions.")
    logger.info("Starting to profile...")
    
    utils = Utilities(log, output)
    utils.metadata()

    # Grouping by operations
    groups = [
        'loads',
        'stores',
        'imm computes',
        'imm shifts',
        'reg computes',
        'reg shifts',
        'jumps',
        'branches',
        "compares",
        "conversions",
        "moves",
        "classifies",
        "csrs",
        "fence",
    ]

    (extension_list, err, err_list) = isaval.get_extension_list(isa)

    for e in err_list:
        logger.error(e)
    if err:
        raise SystemExit(1)
    
    isa_arg = isa.split('I')[0]

    ret_dict, extension_instruction_list, op_dict = instr_groups.group_by_operation(groups, isa_arg, extension_list, master_inst_dict, config, cycle_accurate_config)
    if (len(extension_instruction_list)<=len(master_inst_list)):
        # left_out=[]
        # for i in master_inst_list:
        #     if i not in extension_instruction_list:
        #         left_out.append(i)
        #         print(i)
        logger.warning("Check the extension input.")

    curr_ops_dict = utils.compute_ops_dict(args_list=groups, isa_arg=isa_arg, ext_list=extension_list) 
    
    if 'C' in extension_list:
        logger.warning("riscv-isac does not decode immediate fields for compressed instructions. \
Value based metrics on branch ops may be inaccurate.")

    
    utils.tabulate_stats(ret_dict, header_name='Grouping instructions by Operation')
    ret_dict = instr_groups.privilege_modes(log,config)
    utils.tabulate_stats(ret_dict, header_name='Privilege Mode')

    if cycle_accurate_config != None:

        for metric in config['profiles']['cfg']['metrics']:
            # Finding the new plugin file mentioned in the yaml file
            spec = importlib.util.spec_from_file_location("plugins", f"riscv_application_profiler/plugins/{metric}.py")
            # Converting file to a module
            metric_module = importlib.util.module_from_spec(spec)
            # Importing the module
            spec.loader.exec_module(metric_module)
            
            for funct in config['profiles']['cfg']['metrics'][metric]:
                funct_to_call = getattr(metric_module, funct)
                ret_dict1 = funct_to_call(master_inst_dict, ops_dict=op_dict, extension_used=extension_list, config= config, cycle_accurate_config=cycle_accurate_config)
                utils.tabulate_stats(ret_dict1, header_name=funct)

        # total_cycles = op_dict['total_cycles']
        total_cycles = sum([master_inst_dict[entry] for entry in master_inst_dict]) + cycle_accurate_config['cycles']['reset_cycles']
        print('Total Cycles: ', total_cycles)
        
    else:
        for metric in config['profiles']['cfg']['metrics']:
            # Finding the new plugin file mentioned in the yaml file
            spec = importlib.util.spec_from_file_location("plugins", f"riscv_application_profiler/plugins/{metric}.py")
            # Converting file to a module
            metric_module = importlib.util.module_from_spec(spec)
            # Importing the module
            spec.loader.exec_module(metric_module)
            
            for funct in config['profiles']['cfg']['metrics'][metric]:
                funct_to_call = getattr(metric_module, funct)
                ret_dict1 = funct_to_call(master_inst_dict, ops_dict=op_dict, extension_used=extension_list, config= config, cycle_accurate_config=cycle_accurate_config)
                utils.tabulate_stats(ret_dict1, header_name=funct)
