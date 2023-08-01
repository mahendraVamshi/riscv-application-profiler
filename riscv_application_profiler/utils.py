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

    def tabulate_stats(self, op_dict, counts, metric_name):
        '''
        Tabulates the statistics of the grouped instructions using the tabulate module.

        Args:
            - op_dict: A dictionary with the operations as keys and a list of InstructionEntry
                objects as values.
            - counts: A dictionary with the operations as keys and the number of instructions
                in each group as values.
        '''
        logger.debug("Tabulating statistics.")
        table = []
        for op in op_dict.keys():
            table.append([op, counts[op]])
        self.tables_file.write(f'## {metric_name}\n')

        # create an asciidoc table using pytablewriter from the the data in op_dict
        writer = ptw.AsciiDocTableWriter()
        writer.table_name = ""
        writer.headers = ["Operation", "Count"]
        writer.value_matrix = table
        self.tables_file.write(writer.dumps())

        # self.tables_file.write(tabulate(table, headers=['Operation', 'Count']))
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
    

    def tabulate_stats1(self, op_list, counts, header_name,metric_name):
        '''
        Tabulates the statistics of the grouped instructions using the tabulate module.

        Args:
            - op_dict: A dictionary with the operations as keys and a list of InstructionEntry
                objects as values.
            - counts: A dictionary with the operations as keys and the number of instructions
                in each group as values.
        '''
        logger.debug("Tabulating statistics.")
        table = []
        if len(op_list) > 0:
            name=list(counts[op_list[0]].keys())
        else:
            return 0
        for op in op_list:
            table.append([op])
            for i in name:
                table[-1].append(counts[op][i])

        self.tables_file.write(f'## {metric_name}\n')
        if header_name is None:
            header_name = "Name"
        # create an asciidoc table using pytablewriter from the the data in op_dict
        writer = ptw.AsciiDocTableWriter()
        writer.table_name = ""
        writer.headers = [header_name] + [f"{i}" for i in name]
        writer.value_matrix = table
        self.tables_file.write(writer.dumps())

        # self.tables_file.write(tabulate(table, headers=['Operation', 'Count']))
        self.tables_file.write('\n\n')
        logger.debug("Done.")

    def tabulate_stats_dict (self, in_dict, header_name):

        logger.debug("Tabulating statistics.")
        table = []
        key_list = list(in_dict.keys())
        length=len(in_dict[key_list[0]])
        for i in range(len(in_dict[key_list[0]])):
            table.append([in_dict[key_list[0]][i], in_dict[key_list[1]][i], in_dict[key_list[2]][i], in_dict[key_list[3]][i]])


        self.tables_file.write(f'## {header_name}\n')
        if header_name is None:
            header_name = "Name"
        # create an asciidoc table using pytablewriter from the the data in op_dict
        writer = ptw.AsciiDocTableWriter()
        writer.table_name = ""
        writer.headers = key_list
        writer.value_matrix = table
        self.tables_file.write(writer.dumps())

        # self.tables_file.write(tabulate(table, headers=['Operation', 'Count']))
        self.tables_file.write('\n\n')
        logger.debug("Done.")
