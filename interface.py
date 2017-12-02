import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import *

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
area = DockArea()

pg.setConfigOptions(antialias=True)

win.setCentralWidget(area)
win.resize(1366,768)
win.setWindowTitle("Note Analysis")
win.showMaximized()

# addDock order is nontrivial

controls = Dock("Controls", size=(1,1))
area.addDock(controls, 'bottom')
buttons = pg.LayoutWidget()
controls.addWidget(buttons)

graphs = Dock("Graphs", hideTitle=True)
area.addDock(graphs, 'top', controls)
p1 = pg.PlotWidget(title="Frequencies")
p2 = pg.PlotWidget(title="Onset Detection")
graphs.addWidget(p1)
graphs.addWidget(p2)

progress = Dock("Progress", size=(1, 1))
area.addDock(progress, 'left', controls)
progressBar = QtGui.QProgressBar(enabled=False)
progressBar.setAlignment(QtCore.Qt.AlignCenter)
progressBar.setFormat("Not started yet")
progressBar.setValue(0)
progress.addWidget(progressBar)
progress.layout.setContentsMargins(50,50,50,50)

####

controls.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Maximum)
buttons.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
p1.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
p2.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)                 

####

generalGroup = QtGui.QGroupBox('General')
generalLayout = QtGui.QVBoxLayout()
generalGroup.setLayout(generalLayout)

browse = QtGui.QPushButton('Browse')
cont = QtGui.QPushButton('Continue', enabled=False)

generalLayout.addWidget(browse)
generalLayout.addWidget(cont)

####

thresholdGroup = QtGui.QGroupBox('Threshold', enabled=False)
thresholdLayout = QtGui.QGridLayout()
thresholdGroup.setLayout(thresholdLayout)

up = QtGui.QPushButton('Up')
down = QtGui.QPushButton('Down')
flat = QtGui.QPushButton('Flat')
steep = QtGui.QPushButton('Steep')

thresholdLayout.addWidget(up,0,0)
thresholdLayout.addWidget(down,1,0)
thresholdLayout.addWidget(flat,0,1)
thresholdLayout.addWidget(steep,1,1)

####

paramGroup = QtGui.QGroupBox("Parameters", enabled=False)
paramLayout = QtGui.QGridLayout()
paramGroup.setLayout(paramLayout)

paramLayout.addWidget(QtGui.QLabel("HPS"), 0, 0)
hps = pg.SpinBox(value=3, int=True, bounds=[1, None])
paramLayout.addWidget(hps, 0, 1)

paramLayout.addWidget(QtGui.QLabel("Window Size"), 1, 0)
window = pg.SpinBox(value=12, int=True, bounds=[1, None])
paramLayout.addWidget(window, 1, 1)

addhighpass = QtGui.QCheckBox("Add highpass")
paramLayout.addWidget(addhighpass, 0, 2)

highpass = pg.SpinBox(value=30, int=True, bounds=[1, 20000])
paramLayout.addWidget(highpass, 1, 2)

####

buttons.addWidget(generalGroup, row=0, col=0)
buttons.addWidget(thresholdGroup, row=0, col=2)
buttons.addWidget(paramGroup, row=0, col=3)

file_path = None

def browseClick(self):

    file_dialog = QtGui.QFileDialog()
    file_dialog.setNameFilters(["Wav files (*.wav)"])
    file_dialog.selectNameFilter("Wav files (*.wav)")

    if file_dialog.exec_():

        global file_path
        file_path = file_dialog.selectedFiles()[0]
        paramGroup.setEnabled(True)
        cont.setEnabled(True)
        progressBar.setFormat(file_path)

browse.clicked.connect(browseClick)

firstCont = True
graphs = None

def contButton():

    if firstCont:

        cont.setEnabled(False)
        paramGroup.setEnabled(False)
        progressBar.setEnabled(True)
        progressBar.setMaximum(8)
        i = 0

        import subprocess
        proc = subprocess.Popen(["python", "analyze.py", "-f", file_path, 
                                "-w", str(window.value()), "-p", str(highpass.value()),
                                "-r", str(hps.value()), "-i", "true"],stdout=subprocess.PIPE)

        while proc.poll() is None:

            l = proc.stdout.readline() # This blocks until it receives a newline.
            if l == b'':
                break

            progressBar.setFormat(l.decode('UTF-8'))
            progressBar.setValue(i)
            i += 1
            app.processEvents()

        global graphs

        import pickle
        with open('results.temp','rb') as f:
            graphs = pickle.load(f)
            drawResults()

        import os
        os.remove('results.temp')

cont.clicked.connect(contButton)

def drawResults():

    import internal_utility as iu

    (frequencies, detection) = (graphs[4],  graphs[5])
    (peaks, threshold) = iu.peaks(detection, 5, 1)
    onsets = [ i / len(detection) for i in peaks ]

    maxf = np.amax(frequencies)
    minf = np.amin([i for i in frequencies if i != 0])

    spectrogram = pg.ImageItem(border='w')
    spectrogram.setImage(graphs[3])
    p1.addItem(spectrogram)

    p1.plot(frequencies, pen=pg.mkPen('k', width=2))
    p1.setYRange(minf - 10 if minf>10 else 0, maxf+10)

    p2.plot(detection, pen=pg.mkPen('c', width=2), name="Detection function")
    p2.plot(threshold, pen=pg.mkPen('r', width=2), name="Dynamic Threshold")

    for p in peaks:
        p2.addItem(pg.InfiniteLine(p, pen=pg.mkPen('w', width=1)))

    thresholdGroup.setEnabled(True)

    app.processEvents()

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()