# See LICENCE for licence details.

from riscv_isac.log import *
import pytablewriter as ptw
import os

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