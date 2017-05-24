import matplotlib.pyplot as plt
import numpy as np
import csv

#plt.rcParams['toolbar'] = 'None'

def get_heatmap(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        heatmap = list(reader)

    heatmap = np.array(object=heatmap, dtype=float)
    return heatmap

print('reading values...')

heatmap1 = get_heatmap('spectrogram1.csv')
heatmap2 = get_heatmap('spectrogram2.csv')

print('calculating...')

variances = []

for fourier in heatmap1:
    variances.append(np.var(fourier))

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

ax2.set_ylabel('Frequency Variance')
ax2.plot(variances, 'w-')

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
except:
    pass

plt.show()
