import click
from riscv_application_profiler import __version__

# Top level group named 'cli'
@click.group()
@click.version_option(version=__version__)
def cli():
	'''Command Line Interface for riscv_application_profiler'''

@click.version_option(version=__version__)
# CLI option ''.
# Expects an ISA string.
@click.option(
	'-l',
	'--log',
	help=
	'This option expects the path to an execution log.',
	required=True)
# CLI option 'build_dir'.
# Expects a directory.
@click.option('-o',
			  '--output',
			  help="Path to the output file.",
			  default='./app.profile',
			  show_default=True,
			  required=False)
# CLI function 'generate'
@cli.command()
def profile(log, output):
    '''
    Generates the hardware description of the decoder
    '''
    print("***************************")
    print("RISC-V Application Profiler")
    print("***************************")

    print("Log file: ", log)
    print("Output file: ", output)

    print("***************************")
    print("Profiling the application...\n\n")