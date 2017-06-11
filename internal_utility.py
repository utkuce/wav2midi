import csv
import numpy as np

def get_heatmap(filename):

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        heatmap = list(reader)

    heatmap = np.array(object=heatmap, dtype=float)
    return heatmap

def local_maximas(data):

    maximas = []
    derivative = np.diff(data)

    for i,v in enumerate(derivative):
        if i+1 < len(derivative):
            if v > 0 and derivative[i+1] < 0:
                maximas.append(v)

    return maximas

def peaks(data):

    markers_on = []

    derivative = np.diff(data)
    m = local_maximas(data)
    height_threshold = np.average(m, weights=m)
    
    for i,v in enumerate(derivative):
        if i+1 < len(derivative) and i > 5:
            heigh_enough = data[i] - data[i-5] > height_threshold
            if v > 0 and derivative[i+1] < 0 and heigh_enough:
                markers_on.append(i+1)
         
    return markers_on