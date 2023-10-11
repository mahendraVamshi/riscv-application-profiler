# See LICENSE for licensing information.

# this file is a porting mechanism for using riscv-isac in riscv-application-profiler

from git import Repo
import os
import shutil
import sys

def isac_setup_routine():
    '''
    Sets up the riscv-isac environment.
    '''
    if not os.path.exists('rvop_decoder'):
        os.system('riscv_isac setup')
    sys.path.append(os.path.join(os.getcwd(), 'rvop_decoder'))
