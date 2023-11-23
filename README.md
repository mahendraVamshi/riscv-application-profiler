# RISC-V Application Profiler

The RISC-V Application Profiler is a Python-based tool designed to help software developers optimize the performance of their applications on RISC-V hardware. It works by parsing execution logs and providing insights about the application's behavior. The tool has a modular design, where performance metrics are added as plugins, allowing developers to customize the profiler to their specific needs. The profiler is highly accessible, easy to use, and can be adapted to capture different types of performance metrics. Overall, the RISC-V Application Profiler is a flexible and customizable solution for software developers who want to ensure optimal performance of their applications on RISC-V platforms.

## Installation

Install `pycachesim`. This is a requirement to use the `caches` plugin in the profiler.

```shell
git clone https://github.com/mahendraVamshi/pycachesim.git
cd pycachesim
pip install -e .
cd ..
```

Install `riscv_isac`. This is a development version of isac.
```shell
git clone https://github.com/mahendraVamshi/riscv-isac.git
cd riscv-isac
pip install -e .
cd ..
```

Finally, install the profiler itself.
```shell
git clone https://github.com/mahendraVamshi/riscv-application-profiler.git -b vamshi
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
To profile an application with cycle accurate simulation, run:
```shell
riscv_application_profiler profile --log <path-to-log> --output <path-to-output-directory> --config <path-to-config-file> config.yaml --cycle_accurate_config <path-to-config-file> config.yaml
```

Command line options to the `profile` command:

```text
Options:
  -l, --log TEXT                  This option expects the path to an execution
                                  log.  [required]
  -o, --output TEXT               Path to the output file.  [default: ./build]
  -c, --config TEXT               Path to the YAML configuration file.
                                  [required]
  -ca, --cycle_accurate_config TEXT
                                  Path to the YAML cycle accurate
                                  configuration file.
  -v, --verbose [info|error|debug]
                                  Set verbose level
  --help                          Show this message and exit.
```

Example:

Instruction accurate profiling:
```shell
riscv_application_profiler profile --log ./tests/hello.log --output ./build --config ./sample_config/config.yaml   
```
Cycle accurate profiling:
```shell
riscv_application_profiler profile --log ./tests/hello.log --output ./build --config ./sample_config/config1.yaml  --cycle_accurate_config ./cycle_accurate_config/ca_config.yaml
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
- D$/I$ Hits/Misses/Usage/Utilization. 
