from __future__ import division
import numpy as np
from ctypes import *

class C_Tuple(Structure):
    _fields_ = [("x", c_uint64), ("y", c_uint64)]

class FFI_Spectrogram(Structure):
    _fields_ = [("data", POINTER(POINTER(c_double))), ("shape", C_Tuple)]

class PointerList(Structure):
    _fields_ = [("pointers", c_void_p*6)]

pointerList = PointerList()

def from_ffi(results):
    
    global pointerList
    pointerList = cast(results, POINTER(PointerList)).contents

    spect_list = []

    for i,g in enumerate(pointerList.pointers):
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

def peaks(onset, half_h, c1):

    peaks = []
    maximas_indices = maximas(onset)
    dynamic_threshold = []

    for i in range(half_h, len(onset)-half_h):
        window = onset[i-half_h: i+half_h-1]
        weights = list(range(1,half_h,1)) + list(range(half_h,0,-1))
        dynamic_threshold.append(c1*np.average(window, weights=weights))

    for i in range(5):
        dynamic_threshold.insert(0, dynamic_threshold[0])
    
    i = 0
    while i < len(dynamic_threshold) and i < len(onset):
        if onset[i] > dynamic_threshold[i] and i in maximas_indices:
            if set(range(i-half_h, i+half_h)).isdisjoint(peaks):
                peaks.append(i)
            else:
                for (j,p) in enumerate(peaks):
                    if p in list(range(i-half_h, i+half_h)) and onset[i]>onset[p]:
                        peaks[j] = i
        i+=1    

    return (peaks, dynamic_threshold)

def repeated_notes(peaks, changes, half_h, index_scale):

    repeats = []
    for p in peaks:
        l = range(round((p-half_h)*index_scale), round((p+half_h)*index_scale),1)
        if set(l).isdisjoint(changes):
            repeats.append(p)

    return repeats

def octave_correction(frequencies, wideband):

    corrected = []
    for (index,f) in enumerate(frequencies):

        if f == 0:
            corrected.append(0)
            continue

        i = 2
        current_max = f
        while f*i < wideband.shape[1]/2:
            if wideband[index][f*i] *0.9 > wideband[index][current_max]:
                current_max = f*i
            i += 1

        corrected.append(current_max)

    return corrected