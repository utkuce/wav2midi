# Audio Note Analysis

Converts a monophonic wav file into MIDI

## Requirements

To use, the following must be installed 

  - [Arrayfire Binaries]
  - [CUDA Toolkit]  (Optional)
  - [Python3]  (Not Required for standalone)

If CUDA is not installed it will fall back to OPENCL or CPU

## Usage

Build the [Rust] source as a dynamic library first, if `stft_rust.dll` doesn't exist:
```
$ cargo build
```
then, to analyze a file:
```
$ analyze.py <file_name> [--draw]
```
Replace `analyze.py` with `analyze` for the standalone version

## Standalone

```
$ make
```

will create a standalone distributable folder if [Rust Toolchain][Rust] and [Python3] are installed. `SINGLE_FILE=1` flag will create a single executable file instead of a folder

[Arrayfire Binaries]: <https://arrayfire.com/download/>
[CUDA Toolkit]: <https://developer.nvidia.com/cuda-toolkit>
[Python3]: <https://www.python.org/downloads/>
[Rust]: <https://www.rust-lang.org/en-US/install.html>

