from __future__ import division
import numpy as np
from ctypes import *

class C_Tuple(Structure):
    _fields_ = [("x", c_uint64), ("y", c_uint64)]

class FFI_Spectrogram(Structure):
    _fields_ = [("data", POINTER(POINTER(c_double))), ("shape", C_Tuple)]

class Graphs(Structure):
    _fields_ = [("pointers", c_void_p*6)]

graphs = Graphs()

def from_ffi(results, mylib):
    
    global graphs
    graphs = cast(results, POINTER(Graphs)).contents

    spect_list = []

    for i,g in enumerate(graphs.pointers):
        if i < 4:
            spect_list.append(get_result(g))
        elif i == 4:
            pointer = cast(g, POINTER(c_uint*len(spect_list[3])))
            spect_list.append(np.fromiter(pointer.contents, dtype=np.uint))
        else:
            pointer = cast(g, POINTER(c_double*(len(spect_list[0]-1)) ))
            spect_list.append(np.fromiter(pointer.contents, dtype=float))
        
    return spect_list

def get_result(spect_pointer):

    result = cast(spect_pointer, POINTER(FFI_Spectrogram)).contents

    data = []

    for x in range(0, result.shape.x):
        array_pointer = cast(result.data[x], POINTER(c_double*result.shape.y))
        a = np.frombuffer(array_pointer.contents, dtype=float)
        data.append(a)
    
    return np.asarray(data)

def smooth(dataSet, w):
    return np.convolve(dataSet, np.ones(w)/w)

def maximas(data):

    derivative = np.diff(data)
    maximas = []

    for i in range(1, len(data)-1):
        if data[i] - data[i-1] > 0 and data[i] - data[i+1] > 0:
            maximas.append(i)

    return maximas

def peaks(data, half_h, c1):

    peaks = []
    maximas_indices = maximas(data)
    dynamic_threshold = []

    for i in range(half_h, len(data)-half_h):
        window = data[i-half_h: i+half_h-1]
        weights = list(range(1,half_h,1)) + list(range(half_h,0,-1))
        dynamic_threshold.append(c1*np.average(window, weights=weights))

    for i in range(5):
        dynamic_threshold.insert(0, dynamic_threshold[0])
    
    i = 0
    while i < len(dynamic_threshold):
        if data[i] > dynamic_threshold[i] and i in maximas_indices:
            peaks.append(i)
            i += half_h
        else:
            i+=1

    return (peaks, dynamic_threshold)
