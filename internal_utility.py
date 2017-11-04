from __future__ import division
import numpy as np
from ctypes import *

class C_Tuple(Structure):
    _fields_ = [("x", c_uint64), ("y", c_uint64)]

class FFI_Spectrogram(Structure):
    _fields_ = [("data", POINTER(POINTER(c_double))), ("shape", C_Tuple)]

class Graphs(Structure):
    _fields_ = [("pointers", c_void_p*6)]

stft_rs = cdll.LoadLibrary('target\debug\stft_rust.dll')
stft_rs.analyze.argtypes = [c_void_p]
stft_rs.analyze.restype = c_void_p
stft_rs.clean2d.argtypes = [c_void_p]
stft_rs.clean1d.argtypes = [c_void_p]

ptr = None

def analyze(file_name):
    ptr = stft_rs.analyze(file_name.encode('UTF-8'), True)
    graphs = cast(ptr, POINTER(Graphs)).contents

    spect_list = []

    for i,g in enumerate(graphs.pointers):
        if i < 4:
            spect_list.append(get_result(g))
            stft_rs.clean2d(cast(g, c_void_p)) #data is cloned, original pointer can be cleared
        else:
            if i == 4:
                pointer = cast(g, POINTER(c_uint*len(spect_list[3])))
                spect_list.append(np.fromiter(pointer.contents, dtype=np.uint))
            else:
                pointer = cast(g, POINTER(c_double*(len(spect_list[0]-1)) ))
                spect_list.append(np.fromiter(pointer.contents, dtype=float))
        
            stft_rs.clean1d(cast(g, c_void_p))
        
    return spect_list

result = None

def get_result(spect_pointer):

    result = cast(spect_pointer, POINTER(FFI_Spectrogram)).contents

    data = []

    for x in range(0, result.shape.x):
        array_pointer = cast(result.data[x], POINTER(c_double*result.shape.y))
        a = np.fromiter(array_pointer.contents, dtype=float)
        data.append(a)
    
    return np.asarray(data)

def print_audio_details(fileName):
    stft_rs.print_audio_details(fileName.encode('UTF-8'))

def smooth(dataSet, w):
    return np.convolve(dataSet, np.ones(w)/w)

def maximas(data):

    maximas = []
    derivative = np.diff(data)

    for i in range (0, len(data)-2):
        if derivative[i] > 0 and derivative[i+1] < 0:
            maximas.append(i)

    return maximas