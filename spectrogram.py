import matplotlib.pyplot as plt
import numpy as np
import internal_utility as iu
import sys

import time
start_time = time.time()

iu.print_audio_details(sys.argv[1])
'''
attr1 = iu.STFT_Params(4096, 256)
attr2 = iu.STFT_Params(44100, 2048)

print ('calculating narrowband spectrogram...')
narrowband = iu.stft(sys.argv[1], attr1)
print ('calculating wideband spectrogram...')
wideband = iu.stft(sys.argv[1], attr2)

variances, averages = [], []

for fourier in narrowband:
    variances.append(np.var(fourier))
    averages.append(np.average(fourier))

variances = iu.smooth(variances, 5)
averages = iu.smooth(averages, 5)


print ('combining spectrograms...')

combined = iu.getCombined(sys.argv[1])
print("%s seconds" % int(time.time() - start_time))

print ('calculating harmonic product spectrum...')
hps = iu.hps(combined, 7)
'''

hps = iu.getCombined(sys.argv[1])
print("%s seconds" % int(time.time() - start_time))

frequencies = [np.argmax(n) for n in hps]
iu.write_midi(frequencies, sys.argv[1])

minf = np.amin(frequencies)
maxf = np.amax(frequencies)

#scale = np.divide(wideband.shape[1], narrowband.shape[1])
#lim = [int((minf - 50 if minf>50 else 0)/scale), int((maxf+50)/scale)]

print ('drawing...')

spectrogram1 = np.transpose(hps)
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


#l1, = ax2.plot(variances, '-c', label='variance')
#l2, = ax2.plot(averages, '-w', label='average')
#plt.legend(handles=[l1, l2])

ax3 = fig.add_subplot(2,1,2)
#ax3.set_title('Window Size: {} Step size: {}'.format(attr2.windowSize, attr2.stepSize))
ax3.set_xlabel('Time')
ax3.set_ylabel('Frequency(Hz)')
ax3.imshow(spectrogram2, cmap='inferno', interpolation='nearest', aspect='auto')
ax3.invert_yaxis()

ax3.set_ylim([minf - 50 if minf>50 else 0, maxf+50])

l4, = ax3.plot(frequencies, '-w', label='max')
plt.legend(handles=[l4])

plt.subplots_adjust(left=0.04, bottom=0.05, right=0.97, top=0.97, hspace=0.20)

print("Finished in %s seconds" % int(time.time() - start_time))

try:
    plt.get_current_fig_manager().window.state('zoomed')
    fig.canvas.set_window_title('Music Analysis')
except:
    pass

plt.show()
