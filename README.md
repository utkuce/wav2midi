# Audio Note Analysis

Converts a monophonic wav file into MIDI

## Requirements

To run, the following must be installed 

  - [Arrayfire Binaries]
  - [CUDA Toolkit] <sup>[1]</sup>
  - [Python3] <sup>[2]</sup>

 1. If CUDA is not installed it will fallback to OPENCL or CPU
 2. Not required for standalone version

## Usage

`mylib.dll` must be present in order for it to work. If it is not, first build the [Rust] source as a dynamic library with the following:
```
$ cargo build
```
then, to analyze a file:
```
$ analyze.py [-h] -f FILE_NAME -w WINDOW [-p HIGHPASS] -r HPS_RATE
                  [-o ONSET_WINDOW] [-c THRESHOLD_CONSTANT]
```
Replace `analyze.py` with `analyze` for the standalone version

## Standalone

```
$ make
```

will create a standalone distributable folder if [Rust Toolchain][Rust] and [Python3] are installed. `SINGLE_FILE=1` flag will create a single executable file instead of a folder, but the execution will be slower as everytime files are unpacked into a temporary folder

[Arrayfire Binaries]: <https://arrayfire.com/download/>
[CUDA Toolkit]: <https://developer.nvidia.com/cuda-toolkit>
[Python3]: <https://www.python.org/downloads/>
[Rust]: <https://www.rust-lang.org/en-US/install.html>

