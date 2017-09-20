import matplotlib.pyplot as plt
import numpy as np
import internal_utility as iu
import sys

print('calculating...')
attr1 = iu.Attributes(4096, 256, (16,31))
attr2 = iu.Attributes(44100, 2048, (210, 450))

spectrogram1 = iu.stft(sys.argv[1], attr1)
spectrogram2 = spectrogram1#iu.stft(sys.argv[1], attr2)

variances, averages = [], []

for fourier in spectrogram1:
    variances.append(np.var(fourier))
    averages.append(np.average(fourier))

smoothed_variances = np.convolve(variances, np.ones(5)/5)
smoothed_averages = np.convolve(averages, np.ones(5)/5)

variance_peaks = iu.peaks(smoothed_variances)
average_peaks = iu.peaks(smoothed_averages)

both_peaks = []

for x in variance_peaks:
    if any(n in average_peaks for n in list(range(x-5,x+5))):
        both_peaks.append(x)

#max_frequencies1 = [np.argmax(n) for n in spectrogram1]
max_frequencies2 = [np.argmax(n) for n in spectrogram2]

#transpose
spectrogram1 = [list(x) for x in zip(*spectrogram1)]
spectrogram2 = [list(x) for x in zip(*spectrogram2)]

print ('drawing..')

fig = plt.figure()

ax1 = fig.add_subplot(2,1,1)
ax2 = ax1.twinx()

ax1.set_title('Window Size: {} Step size: {}'.format(attr1.windowSize, attr1.stepSize))
ax1.set_xlabel('Number of Fourier Transforms')
ax1.set_ylabel('Frequency(Hz)')
ax1.imshow(spectrogram1, cmap='inferno', interpolation='nearest', aspect='auto')
ax1.invert_yaxis()

plt.xlim(xmin=0)

ax2.set_xticks(both_peaks)
l1, = ax2.plot(smoothed_variances, '-co', markevery=variance_peaks, label='variance')
l2, = ax2.plot(smoothed_averages, '-wo', markevery=average_peaks, label='average')
#l3, = ax1.plot(max_frequencies1, label='max')
plt.legend(handles=[l1, l2])

ax3 = fig.add_subplot(2,1,2)
ax3.set_title('Window Size: {} Step size: {}'.format(attr2.windowSize, attr2.stepSize))
ax3.set_xlabel('Number of Fourier Transforms')
ax3.set_ylabel('Frequency(Hz)')
ax3.imshow(spectrogram2, cmap='inferno', interpolation='nearest', aspect='auto')
ax3.invert_yaxis()

#ax1.set_ylim([attr1.bandpass[0], attr1.bandpass[1]])
ax3.set_ylim([attr2.bandpass[0], attr2.bandpass[1]])

l4, = ax3.plot(max_frequencies2, label='max')
plt.legend(handles=[l4])

plt.subplots_adjust(left=0.04, bottom=0.05, right=0.97, top=0.97, hspace=0.20)
#fig.tight_layout()

try:
    plt.get_current_fig_manager().window.state('zoomed')
    fig.canvas.set_window_title('Music Analysis')
except:
    pass

plt.show()