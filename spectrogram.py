import matplotlib.pyplot as plt
import numpy as np
import internal_utility as iu
import sys

print('calculating...')

heatmap1 = iu.stft(sys.argv[1], 4096, 512)
print('rhytym analysis complete')
heatmap2 = iu.stft(sys.argv[1], 44100, 2048)
print('pitch analysis complete')

variances, averages = [], []

for fourier in heatmap1:
    variances.append(np.std(fourier))
    averages.append(np.average(fourier))

smoothed_variances = np.convolve(variances, np.ones(5)/5)
smoothed_averages = np.convolve(averages, np.ones(5)/5)

variance_peaks = iu.peaks(smoothed_variances)
average_peaks = iu.peaks(smoothed_averages)

both_peaks = []

for x in variance_peaks:
    if any(n in average_peaks for n in list(range(x-5,x+5))):
        both_peaks.append(x)

max_frequencies1 = [np.argmax(n) for n in heatmap1]
max_frequencies2 = [np.argmax(n) for n in heatmap2]

#transpose
heatmap1 = [list(x) for x in zip(*heatmap1)]
heatmap2 = [list(x) for x in zip(*heatmap2)]

print ('drawing..')

fig = plt.figure()

ax1 = fig.add_subplot(2,1,1)
ax2 = ax1.twinx()

ax1.set_title('Window Size: {} Step size: {}'.format(4096, 512))
ax1.set_xlabel('Number of Fourier Transforms')
ax1.set_ylabel('Frequency(Hz)')
ax1.imshow(heatmap1, cmap='inferno', interpolation='nearest', aspect='auto')
ax1.invert_yaxis()

plt.xlim(xmin=0)

#ax2.plot(variances, '-c')
#ax2.plot(averages, '-w')
ax2.set_xticks(both_peaks)
l1, = ax2.plot(smoothed_variances, '-co', markevery=variance_peaks, label='standard deviation')
l2, = ax2.plot(smoothed_averages, '-wo', markevery=average_peaks, label='average')
l3, = ax1.plot(max_frequencies1, label='max')
plt.legend(handles=[l1, l2, l3])

ax3 = fig.add_subplot(2,1,2)
ax3.set_title('Window Size: {} Step size: {}'.format(44100, 2048))
ax3.set_xlabel('Number of Fourier Transforms')
ax3.set_ylabel('Frequency(Hz)')
ax3.imshow(heatmap2, cmap='inferno', interpolation='nearest', aspect='auto')
ax3.invert_yaxis()

ax1.set_ylim([0,100])
ax3.set_ylim([210,450])

l4, = ax3.plot(max_frequencies2, label='max')
plt.legend(handles=[l4])

plt.subplots_adjust(left=0.04, bottom=0.04, right=0.97, top=0.97, wspace=0.20, hspace=0.25)
#fig.tight_layout()

try:
    plt.get_current_fig_manager().window.state('zoomed')
    fig.canvas.set_window_title('Music Analysis')
except:
    pass

plt.show()