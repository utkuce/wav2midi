import matplotlib.pyplot as plt
import numpy as np
import internal_utility as iu
from ctypes import *

class C_Tuple(Structure):
    _fields_ = [("x", c_uint64), ("y", c_uint64)]

class FFI_Spectrogram(Structure):
    _fields_ = [("data", POINTER(POINTER(c_double))), ("shape", C_Tuple)]

stft = cdll.LoadLibrary('target\debug\stft_rust.dll')
stft.spectrogram.argtypes = [c_char_p, c_uint, c_uint]
stft.spectrogram.restype = c_void_p

result = stft.spectrogram('tetris2.wav'.encode('UTF-8'), 4096, 512)
result = cast(result, POINTER(FFI_Spectrogram)).contents

heatmap = []

for x in range(0, result.shape.x):
    array_pointer = cast(result.data[x], POINTER(c_double*result.shape.y))
    a = np.frombuffer(array_pointer.contents)
    heatmap.append(a)

print('reading values...')

heatmap1 = heatmap# iu.get_heatmap('rhythm.csv')
heatmap2 = iu.get_heatmap('pitch.csv')

print('calculating...')

variances, averages = [], []

for fourier in heatmap1:
    variances.append(np.var(fourier))
    averages.append(np.mean(fourier))

smoothed_variances = np.convolve(variances, np.ones(5)/5)
smoothed_averages = np.convolve(averages, np.ones(5)/5)

variance_peaks = iu.peaks(smoothed_variances)
average_peaks = iu.peaks(smoothed_averages)

both_peaks = []
for x in variance_peaks:
    if any(n in average_peaks for n in list(range(x-5,x+5))):
        both_peaks.append(x)

#transpose
heatmap1 = [list(x) for x in zip(*heatmap1)]
heatmap2 = [list(x) for x in zip(*heatmap2)]

fig = plt.figure()

ax1 = fig.add_subplot(2,1,1)
ax2 = ax1.twinx()

ax1.set_title('Window Size: {} Step size: {}'.format(4096, 512))
ax1.set_xlabel('Number of Fourier Transforms')
ax1.set_ylabel('Frequency(Hz)')
ax1.imshow(heatmap1, cmap='inferno', interpolation='nearest', aspect='auto')
ax1.invert_yaxis()

plt.xlim(xmin=0)

ax2.plot(variances, '-c')
ax2.plot(averages, '-w')
ax2.set_xticks(both_peaks)
l1, = ax2.plot(smoothed_variances, '-o', markevery=variance_peaks, label='varince')
l2, = ax2.plot(smoothed_averages, '-o', markevery=average_peaks, label='averages')
plt.legend(handles=[l1, l2])

ax3 = fig.add_subplot(2,1,2)
ax3.set_title('Window Size: {} Step size: {}'.format(44100, 512))
ax3.set_xlabel('Number of Fourier Transforms')
ax3.set_ylabel('Frequency(Hz)')
ax3.imshow(heatmap2, cmap='inferno', interpolation='nearest', aspect='auto')
ax3.invert_yaxis()

#plt.colorbar(ax1.pcolor(heatmap1, cmap='inferno'))

fig.tight_layout()

try:
    plt.get_current_fig_manager().window.state('zoomed')
    fig.canvas.set_window_title('Music Analysis')
except:
    pass

print ('done.')
plt.show()