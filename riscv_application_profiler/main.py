from pathlib import Path
import click
from riscv_application_profiler import __version__
from riscv_application_profiler.profiler import run
from riscv_isac.log import logger
from riscv_isac.main import setup
import riscv_isac.plugins.spike as isac_spike_plugin
import os
from git import Repo

# Top level group named 'cli'
@click.group()
@click.version_option(version=__version__)
def cli():
	'''Command Line Interface for riscv_application_profiler'''

@click.version_option(version=__version__)
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
	default='./app.profile',
	show_default=True,
	required=False)
@click.option('--verbose', '-v', default='info', help='Set verbose level', type=click.Choice(['info','error','debug'],case_sensitive=False))
# CLI function 'generate'
@cli.command()
def profile(log, output, verbose):
    '''
    Generates the hardware description of the decoder
    '''
    logger.level(verbose)
    logger.info("**********************************")
    logger.info(f"RISC-V Application Profiler v{__version__}")
    logger.info("**********************************")

    log_file = str(Path(log).absolute())
    logger.info(f"\nLog file: {log_file}")
    output_dir = str(Path(output).absolute())
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    logger.info(f"Output directory: {output_dir}")
    if not os.path.exists(f'{output_dir}/riscv-opcodes'):
        logger.info(f'Cloning riscv-opcodes...')
        repo = Repo.clone_from('https://github.com/riscv/riscv-opcodes', f'{output_dir}/riscv-opcodes')
        repo.git.checkout('master')

    # Invoke the actual profiler
    run(log_file, output_dir, verbose)