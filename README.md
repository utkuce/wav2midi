# Audio Note Analysis
---

Converts a monophonic wav file into MIDI

## Requirements

  - [Arrayfire Binaries]
  - [CUDA Toolkit]
  - [Python3]

## Usage

Build the Rust source as a dynamic library with:
```ssh
$ cargo build
```
then to analyze file:
```ssh
$ analyze.py <file_name>
```
or to analyze _and_ draw the results
```ssh
$ spectrogram.py <file_name>
```

[Arrayfire Binaries]: <https://arrayfire.com/download/>
[CUDA Toolkit]: <https://developer.nvidia.com/cuda-toolkit>
[Python3]: <https://www.python.org/downloads/>

