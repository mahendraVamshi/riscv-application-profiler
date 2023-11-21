from pathlib import Path
import shutil
import click
from riscv_application_profiler import __version__
from riscv_application_profiler.profiler import run
from riscv_application_profiler.isac_port import isac_setup_routine
from riscv_isac.log import logger
import riscv_application_profiler.consts
import riscv_isac.plugins.spike as isac_spike_plugin
import os
from git import Repo
import yaml  
#remove later
from riscv_application_profiler.verif import verify

@click.group()
@click.version_option(version=__version__)
def cli():
    '''Command Line Interface for riscv_application_profiler'''

@cli.command()
# CLI option 'log'.
# Expects an ISA string.
@click.option(
	'-l',
	'--log',
	help=
	'This option expects the path to an execution log.',
	required=True)

# CLI option 'output.
# Expects a directory.
@click.option(
	'-o',
	'--output',
	help="Path to the output file.",
	default='./build',
	show_default=True,
	required=False,
    )

# CLI option 'config'.
# Expects a YAML file.
@click.option('-c', '--config', help="Path to the YAML configuration file.", required=True)

# CLI option 'cycle accurate config'.
# Expects a YAML file.
@click.option('-ca', '--cycle_accurate_config', help="Path to the YAML cycle accurate configuration file.", required=False)

# CLI option 'verbose'.
# Expects a string.
@click.option('-v', '--verbose', default='info', help='Set verbose level', type=click.Choice(['info','error','debug'],case_sensitive=False))

# if one has files of log along with latency they can enable check option below 
# required changes for those are commented 
# @click.option('-ch', '--check', help="Path to the dump file which has cycle latency.", required=False)

def profile(config, log, output, verbose, cycle_accurate_config): #, check):
    '''
    Generates the hardware description of the decoder
    '''
    with open(config, 'r') as config_file:
        ia_config = yaml.safe_load(config_file)
    if cycle_accurate_config:
        with open(cycle_accurate_config, 'r') as cycle_accurate_config_file:
            ca_config = yaml.safe_load(cycle_accurate_config_file)
        # if check:
        #     check_file = str(Path(check).absolute())
        #     verify(check_file)
        # else:
        #     check_file = None
    else:
        ca_config = None
    default_commitlog_regex = ia_config['profiles']['cfg']['commitlog_regex']
    default_privilege_mode_regex = ia_config['profiles']['cfg']['privilege_mode_regex']
    isa = ia_config['profiles']['cfg']['isa']
    log_file = str(Path(log).absolute())
    output_dir = str(Path(output).absolute())

    # clone riscv_opcodes and copy decoder plugin
    
    isac_setup_routine()

    logger.level(verbose)
    logger.info("**********************************")
    logger.info(f"RISC-V Application Profiler v{__version__}")
    logger.info("**********************************")
    logger.info("ISA Extension used: " + isa)
    
    logger.info(f"\nLog file: {log_file}")
    logger.info(f"Output directory: {output_dir}")

    # Invoke the actual profiler
    if ca_config != None:
        run(log_file, isa, output_dir, verbose, ia_config, ca_config)# ,check_file)
    else:
        run(log_file, isa, output_dir, verbose, ia_config, None)# ,None)
    logger.info("Done profiling.")
    logger.info(f"Reports in {output_dir}/reports.")

def main():
    cli()

if __name__ == '__main__':
    main()