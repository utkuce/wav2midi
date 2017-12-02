import matplotlib.pyplot as plt
import numpy as np

print ('drawing results...')
plt.switch_backend('TkAgg')

maxf = np.amax(frequencies)
minf = np.amin([i for i in frequencies if i != 0])

fig = plt.figure()

images = []
for i in range(4):
    ax = fig.add_subplot(5,1,i+1)
    ax.imshow(np.transpose(graphs[i]), cmap='inferno', aspect='auto')
    ax.set_ylabel('Frequency(Hz)')
    ax.invert_yaxis()
    ax.set_xticks([])
    images.append(ax)

images[0].set_title('Narrowband')
images[1].set_title('Wideband')
images[2].set_title('Combined')
images[3].set_title('Harmonic Product Spectrum')

scale = np.divide(graphs[1].shape[1], graphs[0].shape[1])
lim = [int((minf - 10 if minf>10 else 0)/scale), int((maxf+10)/scale)]

images[0].set_ylim(lim)
images[1].set_ylim([minf - 10 if minf>10 else 0, maxf+10])
images[2].set_ylim([minf - 10 if minf>10 else 0, maxf+10])
images[3].set_ylim([minf - 10 if minf>10 else 0, maxf+10])

l1, = images[3].plot(frequencies, '-w', label='max')
images[3].set_xlim(xmax=len(frequencies))
images[3].legend(handles=[l1])

ax1 = fig.add_subplot(5,1,5)
ax1.set_yticks([])

l2, = ax1.plot(detection, '-c', label='onset detection')
for tick in ax1.get_xticklabels():
    tick.set_rotation(90)

for p in peaks:
    ax1.axvline(x=p)

l3, = ax1.plot(threshold, '-r', label='dynamic threshold')
ax1.set_xticks(peaks)
ax1.legend(handles=[l2,l3])

ax1.set_title('Onset Detection Function')
ax1.set_xlim(xmin=0, xmax= len(detection))

plt.subplots_adjust(0.04, 0.05, 0.97, 0.97, 0.13, 0.20)

plt.get_current_fig_manager().window.state('zoomed')
fig.canvas.set_window_title('Music Analysis')

plt.show()