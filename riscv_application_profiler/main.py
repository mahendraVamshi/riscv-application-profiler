from pathlib import Path
import shutil
import click
from riscv_application_profiler import __version__
from riscv_application_profiler.profiler import run
from riscv_application_profiler.isac_port import isac_setup_routine
from riscv_isac.log import logger
import riscv_isac.plugins.spike as isac_spike_plugin
import os
from git import Repo
import yaml  

@click.group()
@click.version_option(version=__version__)
def cli():
    '''Command Line Interface for riscv_application_profiler'''

@cli.command()
@click.option('-c', '--config', help="Path to the YAML configuration file.", required=True)
def profile(config):
    '''
    Generates the hardware description of the decoder
    '''
    with open(config, 'r') as config_file:
        config_data = yaml.safe_load(config_file)

    log_file = str(Path(config_data['profiles']['cfg1']['log']).absolute())
    output_dir = os.path.abspath(Path(config_data['profiles']['cfg1']['output']).resolve())

    isac_setup_routine(lib_dir=f'{output_dir}/lib')

    logger.level(config_data['profiles']['cfg1']['verbose'])
    logger.info("**********************************")
    logger.info(f"RISC-V Application Profiler v{__version__}")
    logger.info("**********************************")
    
    logger.info("ISA Extension used: " + config_data['profiles']['cfg1']['isa'])
    logger.info(f"\nLog file: {log_file}")
    logger.info(f"Output directory: {output_dir}")

    run(log_file, config_data['profiles']['cfg1']['isa'], output_dir, config_data['profiles']['cfg1']['verbose'])

    logger.info("Done profiling.")
    logger.info(f"Reports in {output_dir}/reports.")

def main():
    cli()

if __name__ == '__main__':
    main()