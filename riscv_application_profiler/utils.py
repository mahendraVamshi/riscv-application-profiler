# See LICENCE for licence details.

from riscv_isac.log import *
import pytablewriter as ptw
import os
import riscv_application_profiler.consts as consts
import pprint as pp

class Utilities:
    def __init__(self, log, output) -> None:
        os.makedirs(f'{output}/reports', exist_ok=True)
        self.log = log
        self.tables_file = open(f'{output}/reports/tables.adoc', 'w')
        self.tables_file.write(f'# Reports from the RISC-V Application Profiler\n\n')

    def metadata(self):
        '''
        Prints the metadata of the application being profiled.
        '''
        logger.debug("Printing metadata.")
        self.tables_file.write('## Application metadata\n\n')
        self.tables_file.write(f'Execution log file: {self.log}\n\n')
        self.tables_file.write('<Insert other metadata here.>\n\n')
    def print_stats(self, op_dict, counts):
        '''
        Prints the statistics of the grouped instructions.

        Args:
            - op_dict: A dictionary with the operations as keys and a list of InstructionEntry
                objects as values.
            - counts: A dictionary with the operations as keys and the number of instructions
                in each group as values.
        '''
        logger.debug("Printing statistics.")
        for op in op_dict.keys():
            logger.info(f'{op}: {counts[op]}')
        logger.debug("Done.")

    def tabulate_stats (self, in_dict, header_name):

        logger.debug("Tabulating statistics.")
        table = []
        if in_dict == None:
            logger.error("Dictionary is empty.")
            exit(1)
        key_list = list(in_dict.keys())
        length=len(key_list)
        for i in range(len(in_dict[key_list[0]])):
            l1=[]
            for j in range(length):
                l1.append(in_dict[key_list[j]][i])
            table.append(l1)


        self.tables_file.write(f'## {header_name}\n')
        if header_name is None:
            header_name = "Name"
        writer = ptw.AsciiDocTableWriter()
        writer.table_name = ""
        writer.headers = key_list
        writer.value_matrix = table
        self.tables_file.write(writer.dumps())

        self.tables_file.write('\n\n')
        logger.debug("Done.")

    def remove_dups(self, target: list) -> list:
        '''
        Removes duplicates from a list.

        Args:
            - target: The list to remove duplicates from.

        Returns:
            - A list with no duplicates.
        '''
        temp_list = []
        for entry in target:
            if entry not in temp_list:
                temp_list.append(entry)
        return temp_list

    def compute_ops_dict(self, args_list: list, ext_list: list, isa_arg: str) -> dict:
        '''
        compute the current ops dict out of the master ops db
        
        Args:
            - ext_list: A list of extensions to be supported.
            - isa_arg: The ISA to be supported.
        
        Returns:
            - A dictionary containing the supported operations.
        '''

        temp_ops_dict = {entry:[] for entry in args_list}
        if isa_arg == 'RV32':
            master_ops_dict = consts.ops_dict['RV32']
        elif isa_arg == 'RV64':
            master_ops_dict = consts.ops_dict['RV32']
            for ext in ext_list:
                for op_type in args_list:
                    master_ops_dict[ext][op_type].extend(consts.ops_dict['RV64'][ext][op_type])
        else:
            logger.error(f'XLEN {isa_arg} not supported.')
            exit(1)
        for ext in ext_list:
            for op_type in args_list:
                temp_ops_dict[op_type] += master_ops_dict[ext][op_type]
        result_dict = {entry:self.remove_dups(temp_ops_dict[entry]) for entry in temp_ops_dict}
        return result_dict
    

    
