import matplotlib.pyplot as plt
import numpy as np
import csv

#plt.rcParams['toolbar'] = 'None'

try:
  plt.get_current_fig_manager().window.state('zoomed')
except: 
  pass

with open('spectrogram.csv', 'r') as file:
    reader = csv.reader(file)
    heatmap = list(reader)

heatmap = np.array(object=heatmap, dtype=float)

averages = []

for fourier in heatmap:
  total = 0
  for frequency, amplitude in enumerate(fourier):
    total += frequency*amplitude
  averages.append(total/len(fourier))

heatmap = [list(x) for x in zip(*heatmap)]

ax1 = plt.gca()
ax2 = ax1.twinx()

ax1.set_xlabel('Number of Fourier Transforms')
ax1.set_ylabel('Frequency(Hz)')
ax1.imshow(heatmap, cmap='inferno', interpolation='nearest', aspect='auto')
ax1.invert_yaxis()

ax2.set_ylabel('Weighed Average Frequency')
ax2.plot(averages, 'w-')

plt.show()
