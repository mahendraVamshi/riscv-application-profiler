# See LICENSE for licensing information.

# this file is a porting mechanism for using riscv-isac in riscv-application-profiler

from git import Repo
import os
import shutil
import sys

def repo_setup(url, lib, branch):
    '''
    Clones the repository and checks out the specified branch.
    '''
    repo = Repo.clone_from(url, f'{lib}/')
    repo.git.checkout(branch)
    return repo

def isac_setup_routine(lib_dir):
    '''
    Sets up the riscv-isac environment.
    '''

    os.makedirs(lib_dir, exist_ok=True)

    # Clone the riscv-isac repository
    isac_repo = repo_setup('https://github.com/riscv-software-src/riscv-isac.git', lib_dir, '0.17.0')

    constants_file = os.path.join(os.getcwd(),  f'{lib_dir}/riscv_isac/data/constants.py')
    plugin_file = os.path.join(os.getcwd(),  f'{lib_dir}/riscv_isac/data/rvopcodesdecoder.py')

    shutil.copy(plugin_file,lib_dir)
    shutil.copy(constants_file,lib_dir)

    opcodes_repo = repo_setup('https://github.com/riscv/riscv-opcodes.git', f'{lib_dir}/riscv_opcodes', 'master')

    # remove .git
    shutil.rmtree(f'{lib_dir}/.git')

    # add the library to the search path
    sys.path.append(lib_dir)