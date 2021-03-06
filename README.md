# Audio Note Analysis

Converts a monophonic wav file into a MIDI file. A more in depth explanation can be found [here](screenshots/poster.png) 

## Requirements

To run, the following must be installed 

  - [Arrayfire Binaries] ( Last tested with 3.6.2 )
  - [CUDA Toolkit]
    - If CUDA is not installed it should fallback to OpenCL or CPU
  - [Python3]
    - Required python packages:
```
pip install --user numpy PyQt5 pyqtgraph matplotlib
```
  
 - Make sure that the CUDA and Arrayfire Environment Variables are set correctly

## Build

First build the [Rust] source <sup>[1]</sup> as a dynamic library to create `wav2midi.dll` with the following:

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

![gui](screenshots/interface.png)

## Standalone (CLI only)

```
$ make
```

will create a standalone distributable folder if [Rust Toolchain][Rust] and [Python3] are installed. `SINGLE_FILE=1` flag will create a single executable file instead of a folder, but the execution will be slower as everytime files are unpacked into a temporary folder

## Sample output example

- testaudio/tetris_acoustic_guitar.wav → testaudio/tetris_acoustic_guitar.mid
```
analyze.py -f testaudio/tetris_acoustic_guitar.wav -w 13 -p 215 -r 3 -o 7 -c 1.03
```
- testaudio/tetris_violin.wav → testaudio/tetris_violin.mid
```
analyze.py -f testaudio/tetris_violin.wav -w 13 -p 215 -r 6 -o 7 -c 1.02
```

![spectrograms](screenshots/spectrograms.png)

[Arrayfire Binaries]: <https://arrayfire.com/download/>
[CUDA Toolkit]: <https://developer.nvidia.com/cuda-toolkit>
[Python3]: <https://www.python.org/downloads/>
[Rust]: <https://www.rust-lang.org/en-US/install.html>

