import matplotlib.pyplot as plt
import numpy as np
import csv

plt.rcParams['toolbar'] = 'None'

try:
  plt.get_current_fig_manager().window.state('zoomed')
except: 
  pass

with open('spectogram.csv', 'r') as file:
    reader = csv.reader(file)
    heatmap = list(reader)

heatmap = np.array(object=heatmap, dtype=float)
heatmap = [list(x) for x in zip(*heatmap)]
plt.imshow(heatmap, cmap='inferno', interpolation='nearest', aspect='auto')
plt.show()
