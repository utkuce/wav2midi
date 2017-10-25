import matplotlib.pyplot as plt
import numpy as np
import internal_utility as iu
import sys

import time
start_time = time.time()

spectrogram_list = iu.analyze(sys.argv[1])

variances, averages = [], []

for fourier in spectrogram_list[0]:
    variances.append(np.var(fourier))
    averages.append(np.average(fourier))

variances = iu.smooth(variances, 5)
averages = iu.smooth(averages, 5)

frequencies = [np.argmax(n) for n in spectrogram_list[3]]

minf = np.amin(frequencies)
maxf = np.amax(frequencies)

print ('drawing...')

fig = plt.figure()

ax1 = fig.add_subplot(4,1,1)
ax2 = ax1.twinx()

ax1.set_title('Narrowband')
#ax1.set_xlabel('Time')
ax1.set_ylabel('Frequency(Hz)')
ax1.imshow(np.transpose(spectrogram_list[0]), cmap='inferno', interpolation='nearest', aspect='auto')
ax1.invert_yaxis()

plt.xlim(xmin=0)

#l1, = ax2.plot(variances, '-c', label='variance')
#l2, = ax2.plot(averages, '-w', label='average')
#plt.legend(handles=[l1, l2])

ax3 = fig.add_subplot(4,1,2)
ax3.set_title('Wideband')
#ax3.set_xlabel('Time')
ax3.set_ylabel('Frequency(Hz)')
ax3.imshow(np.transpose(spectrogram_list[1]), cmap='inferno', interpolation='nearest', aspect='auto')
ax3.invert_yaxis()

ax4 = fig.add_subplot(4,1,3)
ax4.set_title('Combined')
#ax4.set_xlabel('Time')
ax4.set_ylabel('Frequency(Hz)')
ax4.imshow(np.transpose(spectrogram_list[2]), cmap='inferno', interpolation='nearest', aspect='auto')
ax4.invert_yaxis()

ax5 = fig.add_subplot(4,1,4)
ax5.set_title('Harmonic Product Spectrum')
ax5.set_xlabel('Time')
ax5.set_ylabel('Frequency(Hz)')
ax5.imshow(np.transpose(spectrogram_list[3]), cmap='inferno', interpolation='nearest', aspect='auto')
ax5.invert_yaxis()

scale = np.divide(spectrogram_list[1].shape[1], spectrogram_list[0].shape[1])
lim = [int((minf - 50 if minf>50 else 0)/scale), int((maxf+50)/scale)]

ax1.set_ylim(lim)
ax3.set_ylim([minf - 50 if minf>50 else 0, maxf+50])
ax4.set_ylim([minf - 50 if minf>50 else 0, maxf+50])
ax5.set_ylim([minf - 50 if minf>50 else 0, maxf+50])

l4, = ax5.plot(frequencies, '-w', label='max')
plt.legend(handles=[l4])

plt.subplots_adjust(left=0.03, bottom=0.05, right=0.99, top=0.97, hspace=0.20, wspace=0.13)

print("Finished in %s seconds" % int(time.time() - start_time))

try:
    plt.get_current_fig_manager().window.state('zoomed')
    fig.canvas.set_window_title('Music Analysis')
except:
    pass

plt.show()
