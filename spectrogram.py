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

heatmap1 = get_heatmap('rhythm.csv')
heatmap2 = get_heatmap('pitch.csv')

print('calculating...')

variances = []
averages = []

for fourier in heatmap1:
    variances.append(np.var(fourier))
    averages.append(np.mean(fourier))

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

l1, = ax2.plot(variances, '-c', label='variance')
l2, = ax2.plot(averages, '-w', label='average amplitude')
plt.legend(handles=[l1, l2])

def peaks(data):
    markers_on = []
    derivative = np.diff(data) 
    for i,v in enumerate(derivative):
        if i+1 < len(derivative) and i > 5:
            if v > 0 and derivative[i+1] < 0 and data[i] - data[i-5] > 0.1:
                markers_on.append(i+1)
    return markers_on

smoothed_variances = np.convolve(variances, np.ones(5)/5)
smoothed_averages = np.convolve(averages, np.ones(5)/5)

a = peaks(smoothed_variances)
b = peaks(smoothed_averages)

ax2.plot(smoothed_variances, '-o', markevery=a)
ax2.plot(smoothed_averages, '-o', markevery=b)

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
