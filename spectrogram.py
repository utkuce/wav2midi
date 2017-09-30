import matplotlib.pyplot as plt
import numpy as np
import internal_utility as iu
import sys

import time
start_time = time.time()

attr1 = iu.STFT_Params(4096, 2048)
attr2 = iu.STFT_Params(44100, 2048)

print ('calculating narrowband spectrogram...')
narrowband = iu.stft(sys.argv[1], attr1)
print ('calculating wideband spectrogram...')
wideband = iu.stft(sys.argv[1], attr2)

variances, averages = [], []

for fourier in narrowband:
    variances.append(np.var(fourier))
    averages.append(np.average(fourier))

#variances = iu.smooth(variances)
#averages = iu.smooth(averages)

print ('combining spectrograms...')
combined = iu.combine(narrowband, wideband)

print ('calculating harmonic product spectrum...')
hps = iu.hps(combined, 5)

max_frequencies2 = [np.argmax(n) for n in hps]

'''
v = np.trim_zeros(variances)

x = range(len(v))
xp = np.arange(len(wideband[0])) * int(len(x)/len(wideband[0]))
interpolated = np.ndarray((len(wideband), len(x)))
for i in range(len(wideband)):
    interpolated[i] = np.interp(x, xp, wideband[i])

wideband = interpolated

wideband = np.transpose(wideband)
#v /= np.amax(v)
# for i in range(wideband.shape[0]):
#     wideband[i] *= v[i]
max_frequencies1 = [np.argmax(n) for n in filter_guess]
wideband = np.transpose(wideband)
'''
print ('drawing...')

spectrogram1 = np.transpose(narrowband)
spectrogram2 = np.transpose(hps)

fig = plt.figure()

ax1 = fig.add_subplot(2,1,1)
ax2 = ax1.twinx()

#ax1.set_title('Window Size: {} Step size: {}'.format(attr1.windowSize, attr1.stepSize))
ax1.set_xlabel('Time')
ax1.set_ylabel('Frequency(Hz)')
ax1.imshow(spectrogram1, cmap='inferno', interpolation='nearest', aspect='auto')
ax1.invert_yaxis()

plt.xlim(xmin=0)

l1, = ax2.plot(variances, '-c', label='variance')
l2, = ax2.plot(averages, '-w', label='average')
#l3, = ax1.plot(max_frequencies1, label='max')
plt.legend(handles=[l1, l2])

ax3 = fig.add_subplot(2,1,2)
#ax3.set_title('Window Size: {} Step size: {}'.format(attr2.windowSize, attr2.stepSize))
ax3.set_xlabel('Time')
ax3.set_ylabel('Frequency(Hz)')
ax3.imshow(spectrogram2, cmap='inferno', interpolation='nearest', aspect='auto')
ax3.invert_yaxis()

#ax1.set_ylim([attr1.bandpass[0]/10.76, attr1.bandpass[1]/10.76])
#ax3.set_ylim([attr2.bandpass[0], attr2.bandpass[1]])
ax1.set_ylim([0,1250])
ax3.set_ylim([0,1250])

l4, = ax3.plot(max_frequencies2, '-w', label='max')
plt.legend(handles=[l4])

plt.subplots_adjust(left=0.04, bottom=0.05, right=0.97, top=0.97, hspace=0.20)
#fig.tight_layout()

print("Finished in %s seconds" % int(time.time() - start_time))

try:
    plt.get_current_fig_manager().window.state('zoomed')
    fig.canvas.set_window_title('Music Analysis')
except:
    pass

plt.show()
