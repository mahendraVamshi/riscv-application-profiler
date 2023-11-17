# RISC-V Application Profiler

The RISC-V Application Profiler is a Python-based tool designed to help software developers optimize the performance of their applications on RISC-V hardware. It works by parsing execution logs and providing insights about the application's behavior. The tool has a modular design, where performance metrics are added as plugins, allowing developers to customize the profiler to their specific needs. The profiler is highly accessible, easy to use, and can be adapted to capture different types of performance metrics. Overall, the RISC-V Application Profiler is a flexible and customizable solution for software developers who want to ensure optimal performance of their applications on RISC-V platforms.

## Installation

```shell
git clone https://github.com/mahendraVamshi/pycachesim.git
cd pycachesim
pip install -e .
```

```shell
git clone https://github.com/mahendraVamshi/riscv-isac.git
cd riscv-isac
pip install -e .
```

```shell
git clone https://github.com/mahendraVamshi/riscv-application-profiler.git
cd riscv-application-profiler
pip install -e .
```

## Usage

To display the help message, run:
```shell
riscv_application_profiler --help
riscv_application_profiler profile --help
```

To generate a log file, run:
```shell
spike --log-commits <path-to-binary>
```

**NOTE**: You need to use ``--enable-commitlog`` while configuring [spike](https://github.com/riscv-software-src/riscv-isa-sim#build-steps).

To profile an application, run:
```shell
riscv_application_profiler profile --log <path-to-log> --output <path-to-output-directory> --config <path-to-config-file> config.yaml
```
```shell
riscv_application_profiler profile --log <path-to-log> --output <path-to-output-directory> --config <path-to-config-file> config.yaml --cycle_accurate_config <path-to-config-file> config.yaml
```

Command line arguements:

```text
-l, --log   [required]: Path to the log file generated by spike.
-o, --output [optional]: Path to the output files.
-c, --config   [required]: Path to the configuration YAML file.
```

Example:

Instruction accurate profiling:
```shell
riscv_application_profiler profile --log ./tests/hello_world_ed.dump --output ./build --config ./sample_config/config.yaml   
```
Cycle accurate profiling:
```shell
riscv_application_profiler profile --log ./tests/hello.log --output ./build --config ./sample_config/config.yaml --cycle_accurate_config ./cycle_accurate_config/ca1.yaml 
```

**Note**: The log file should be an execution log generated using spike as of today. Support for configuring log formats will be added in the future.

## Features

The profiler supports the following list of features as plugins:

Grouping instructions by:
- Type of operation performed.
- Privilege mode used for execution.
- Directions and Sizes (for jumps/branches).

Lists:
- Presence of Nested Loops.
- Store-Load bypass.
- Presence of RAW dependencies.
- Pattern detection for custom instructions.

Histogram for:
- RegisterFile (XRF/FRF) usage.
- CSR accesses.
- D$/I$ Hits/Misses/Usage. 