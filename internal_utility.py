from __future__ import division
import numpy as np
from ctypes import *

class STFT_Params():
    def __init__(self, windowSize, stepSize):
        self.windowSize = windowSize
        self.stepSize = stepSize

class C_Tuple(Structure):
    _fields_ = [("x", c_uint64), ("y", c_uint64)]

class FFI_Spectrogram(Structure):
    _fields_ = [("data", POINTER(POINTER(c_double))), ("shape", C_Tuple)]

stft_rs = cdll.LoadLibrary('target\debug\stft_rust.dll')
stft_rs.spectrogram.argtypes = [c_char_p, c_uint, c_uint]
stft_rs.spectrogram.restype = c_void_p
stft_rs.clean.argtypes = [c_void_p]

ptr = None

def stft(fileName, params):

    ptr = stft_rs.spectrogram(fileName.encode('UTF-8'), params.windowSize, params.stepSize)
    result = cast(ptr, POINTER(FFI_Spectrogram)).contents

    data = []

    for x in range(0, result.shape.x):
        array_pointer = cast(result.data[x], POINTER(c_double*result.shape.y))
        a = np.fromiter(array_pointer.contents, dtype=float)
        data.append(a)
    
    stft_rs.clean(cast(ptr, c_void_p)) #data is cloned, original pointer can be deleted
    return np.asarray(data)

def combine(narrowband, wideband):

    combined = np.ndarray(shape=wideband.shape)
    scale = np.divide(wideband.shape, narrowband.shape)
    for (x,y), value in np.ndenumerate(wideband):
        combined[x,y] = (value * narrowband[int(x/scale[0]), int(y/scale[1])])**0.5
    
    return combined

def downsample(data, rate):    
    return data.reshape( (-1, rate) ).mean(axis=1)

def hps(data, m_rate):
    hps = np.copy(data)
    for i in range(m_rate, 1, -1):
        downsampled = []
        for row in data:
            while len(row) % i != 0:
                row = np.append(row,0)
            downsampled.append(downsample(row, i))
        for (x,y), value in np.ndenumerate(downsampled):
            hps[x,y] *= value

    return hps

def smooth(dataSet):
    w = 25
    return np.convolve(dataSet, np.ones(w)/w)

def maximas(data):

    maximas = []
    derivative = np.diff(data)

    for i in range (0, len(data)-2):
        if derivative[i] > 0 and derivative[i+1] < 0:
            maximas.append(i)

    return maximas