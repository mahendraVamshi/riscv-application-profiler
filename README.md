# RISC-V Application Profiler

The RISC-V Application Profiler is a Python-based tool designed to help software developers optimize the performance of their applications on RISC-V hardware. It works by parsing execution logs and providing insights about the application's behavior. The tool has a modular design, where performance metrics are added as plugins, allowing developers to customize the profiler to their specific needs. The profiler is highly accessible, easy to use, and can be adapted to capture different types of performance metrics. Overall, the RISC-V Application Profiler is a flexible and customizable solution for software developers who want to ensure optimal performance of their applications on RISC-V platforms.

Detailed documentation can be found [here](https://riscv-application-profiler.readthedocs.io/en/latest/).

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
To profile an application with cycle accurate simulation, run:
```shell
riscv_application_profiler profile --log <path-to-log> --output <path-to-output-directory> --config <path-to-config-file> config.yaml --cycle_accurate_config <path-to-config-file> config.yaml
```
**Info**:

Path to the log file is mandatory. Example log files can be found in the `sample_artifacts/logs` directory.

Path to the output directory is optional. If not provided, the profiler will create a directory named `build` in the current working directory.

Path to the config file is mandatory. Example `config.yaml` is located in `sample_configs/profiler_config` directory. L2 cache config files are located in `sample_configs/profiler_config/L2_configs` directory. 

Path to the cycle accurate config file is optional. Example `config.yaml` is located in `sample_configs/cycle_accurate` directory. Use this option only if you want to profile an application with cycle accurate simulation. L2 cache config files are located in `sample_configs/cycle_accurate/L2_configs` directory.

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

To profile an application, run:

```shell
riscv_application_profiler profile --log ./sample_artifacts/logs/hello.log --output ./build --config ./sample_configs/profiler_config/config.yaml   
```
To profile an application with cycle accurate simulation, run:

```shell
riscv_application_profiler profile --log ./sample_artifacts/logs/hello.log --output ./build --config ./sample_configs/profiler_config/L2_configs/config.yaml --cycle_accurate_config ./sample_configs/cycle_accurate/L2_configs/config.yaml 
```

**Note**: The log file should be an execution log generated using spike as of today. Support for configuring log formats will be added in the future.

**Note**: Metrics such as grouping instructs by operation and privledge mode are hard coded in the profiler.py file as the input to these functions is the commit log. However, the metrics such as grouping instructs by CSRs and cache computation is mandatory for a cycle accurate profiling.

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
- Unifed L2 Cache Hits/Misses/Usage/Utilization.
