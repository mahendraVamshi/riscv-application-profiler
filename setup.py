"""The setup script."""

import os
from setuptools import setup, find_packages
import codecs

# Base directory of package
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()
def read_requires():
    with open(os.path.join(here, "riscv_application_profiler/requirements.txt"),
              "r") as reqfile:
        return reqfile.read().splitlines()


# Long Description
with open("README.md", "r") as fh:
    readme = fh.read()

setup_requirements = []

test_requirements = []

setup(
    name='riscv-application-profiler',
    version='1.0.0',
    description="RISC-V Application Profiler",
    long_description=readme + '\n\n',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta"
    ],
    url='https://github.com/mahendraVamshi/riscv-application-profiler',
    author="PES University + InCore Semiconductors",
    author_email='',
    license="BSD-3-Clause",
    packages=find_packages(),
    package_dir={'riscv_application_profiler': 'riscv_application_profiler'},
    package_data={'riscv_application_profiler': ['requirements.txt']},
    install_requires=read_requires(),
    python_requires='>=3.7.0',
    entry_points={
        'console_scripts': ['riscv_application_profiler=riscv_application_profiler.main:cli'],
    },
    include_package_data=True,
    keywords='riscv_application_profiler',
    tests_require=test_requirements,
    zip_safe=False,
)
