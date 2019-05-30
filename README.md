# Audio Note Analysis

Converts a monophonic wav file into MIDI

## Requirements

To run, the following must be installed 

  - [Arrayfire Binaries] 
  - [CUDA Toolkit] <sup>[1]</sup> 
  - [Python3] <sup>[2]</sup> 

 1. If CUDA is not installed it should fallback to OpenCL or CPU
 2. Required python packages:
  
  ```
  pip install --user numpy PyQt5 pyqtgraph matplotlib
  ```

 Make sure that the CUDA and Arrayfire Environment Variables are set correctly

## Build

First build the [Rust] source <sup>[1]</sup> as a dynamic library to create `mylib.dll` with the following:

```
$ cargo +nightly build
```

 1. Dependency `synthrs` requires nightly toolchain: 
 ```
 $ rustup install nightly
 ```
## Usage
```
$ analyze.py [-h] -f FILE_NAME [-w WINDOW] [-p HIGHPASS] [-r HPS_RATE]
          [-o ONSET_WINDOW] [-c THRESHOLD_CONSTANT] [-i] [-n]
```

OR

```interface.py``` provides a GUI

![gui](https://raw.githubusercontent.com/utkuce/wav2midi/master/interface.png)

## Standalone (CLI only)

```
$ make
```

will create a standalone distributable folder if [Rust Toolchain][Rust] and [Python3] are installed. `SINGLE_FILE=1` flag will create a single executable file instead of a folder, but the execution will be slower as everytime files are unpacked into a temporary folder

[Arrayfire Binaries]: <https://arrayfire.com/download/>
[CUDA Toolkit]: <https://developer.nvidia.com/cuda-toolkit>
[Python3]: <https://www.python.org/downloads/>
[Rust]: <https://www.rust-lang.org/en-US/install.html>

