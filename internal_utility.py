import csv
import numpy as np
from ctypes import *

class C_Tuple(Structure):
    _fields_ = [("x", c_uint64), ("y", c_uint64)]

class FFI_Spectrogram(Structure):
    _fields_ = [("data", POINTER(POINTER(c_double))), ("shape", C_Tuple)]

stft_rs = cdll.LoadLibrary('target\debug\stft_rust.dll')
stft_rs.spectrogram.argtypes = [c_char_p, c_uint, c_uint]
stft_rs.spectrogram.restype = c_void_p

def stft(fileName, windowSize, stepSize):

    result = stft_rs.spectrogram(fileName.encode('UTF-8'), windowSize, stepSize)
    result = cast(result, POINTER(FFI_Spectrogram)).contents

    data = []

    for x in range(0, result.shape.x):
        array_pointer = cast(result.data[x], POINTER(c_double*result.shape.y))
        a = np.frombuffer(array_pointer.contents)
        data.append(a)

    return data

def get_heatmap(filename):

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        heatmap = list(reader)

    heatmap = np.array(object=heatmap, dtype=float)
    return heatmap

def local_maximas(data):

    maximas = []
    derivative = np.diff(data)

    for i,v in enumerate(derivative):
        if i+1 < len(derivative):
            if v > 0 and derivative[i+1] < 0:
                maximas.append(v)

    return maximas

def peaks(data):

    markers_on = []

    derivative = np.diff(data)
    m = local_maximas(data)
    height_threshold = np.average(m, weights=m)
    
    for i,v in enumerate(derivative):
        if i+1 < len(derivative) and i > 5:
            heigh_enough = data[i] - data[i-5] > height_threshold
            if v > 0 and derivative[i+1] < 0 and heigh_enough:
                markers_on.append(i+1)
         
    return markers_on