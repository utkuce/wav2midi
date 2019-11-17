import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.dockarea import *
import os
import internal_utility as iu


app = QtGui.QApplication([])
win = QtGui.QMainWindow()
area = DockArea()

pg.setConfigOptions(antialias=True)

win.setCentralWidget(area)
win.resize(1366,768)
win.setWindowTitle("Wav To Midi ♫")
win.showMaximized()

# addDock order is nontrivial

controls = Dock("Controls", size=(1,1))
area.addDock(controls, 'bottom')
buttons = pg.LayoutWidget()
controls.addWidget(buttons)

graphsDock1 = Dock("Graphs Tab1")
area.addDock(graphsDock1, 'top', controls)
p1 = pg.PlotWidget(title="Frequencies")
p2 = pg.PlotWidget(title="Onset Detection")
graphsDock1.addWidget(p1)
graphsDock1.addWidget(p2)
graphsDock1.layout.setContentsMargins(5,5,5,5)

progressDock = Dock("Progress", size=(1, 1))
area.addDock(progressDock, 'left', controls)

progressBar = QtGui.QProgressBar(enabled=False)
progressBar.setAlignment(QtCore.Qt.AlignCenter)
progressBar.setFormat("Not started yet")
progressBar.setValue(0)

progressDock.addWidget(progressBar)
progressDock.layout.setContentsMargins(50,50,50,50)

graphsDock2 = Dock("Graphs Tab2")
area.addDock(graphsDock2, 'below', graphsDock1)
p3 = pg.PlotWidget(title="Narrowband Spectrogram")
graphsDock2.addWidget(p3)
graphsDock2.layout.setContentsMargins(5,5,5,5)

graphsDock3 = Dock("Graphs Tab3")
area.addDock(graphsDock3, 'below', graphsDock2)
p4 = pg.PlotWidget(title="Wideband Spectrogram")
graphsDock3.addWidget(p4)
graphsDock3.layout.setContentsMargins(5,5,5,5)

area.moveDock(graphsDock1, 'above', graphsDock2)

####

controls.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Maximum)
buttons.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
p1.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
p2.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)                 

####

generalGroup = QtGui.QGroupBox('General')
generalLayout = QtGui.QVBoxLayout()
generalGroup.setLayout(generalLayout)

browse = QtGui.QPushButton('Select File')
analyze = QtGui.QPushButton('Analyze', enabled=False)
midi = QtGui.QPushButton('Create MIDI', enabled=False)

generalLayout.addWidget(browse)
generalLayout.addWidget(analyze)
generalLayout.addWidget(midi)

####

thresholdGroup = QtGui.QGroupBox('Threshold', enabled=False)
thresholdLayout = QtGui.QGridLayout()
thresholdGroup.setLayout(thresholdLayout)

up = QtGui.QPushButton('Up')
down = QtGui.QPushButton('Down')
flat = QtGui.QPushButton('Flat')
steep = QtGui.QPushButton('Steep')

cLabel = QtGui.QLabel('c = 1.05')
hLabel = QtGui.QLabel('half_h = 5')
cLabel.setAlignment(QtCore.Qt.AlignCenter)
hLabel.setAlignment(QtCore.Qt.AlignCenter)

thresholdLayout.addWidget(up,0,0)
thresholdLayout.addWidget(down,1,0)
thresholdLayout.addWidget(cLabel,2,0)

thresholdLayout.addWidget(flat,0,1)
thresholdLayout.addWidget(steep,1,1)
thresholdLayout.addWidget(hLabel,2,1)

####

paramGroup = QtGui.QGroupBox("Parameters", enabled=False)
paramLayout = QtGui.QGridLayout()
paramGroup.setLayout(paramLayout)

paramLayout.addWidget(QtGui.QLabel("HPS Rate"), 0, 0)
hps = pg.SpinBox(value=3, int=True, bounds=[1, None], step=1)
paramLayout.addWidget(hps, 0, 1)

paramLayout.addWidget(QtGui.QLabel("Window Size"), 1, 0)
window = pg.SpinBox(value=13, int=True, bounds=[1, None], step=1)
paramLayout.addWidget(window, 1, 1)

paramLayout.addWidget(QtGui.QLabel("Highpass"), 2, 0)
highpass = pg.SpinBox(value=30, int=True, bounds=[1, 20000], step=10)
highpass.setAccelerated(True)
paramLayout.addWidget(highpass, 2, 1)

####

optionsGroup = QtGui.QGroupBox("Options", enabled=False)
optionsLayout = QtGui.QGridLayout()
optionsGroup.setLayout(optionsLayout)

onsetCheck = QtGui.QCheckBox("Onset Detection", checked=True)
optionsLayout.addWidget(onsetCheck)

begCheck = QtGui.QCheckBox("Replace beginning\nwith silence")
optionsLayout.addWidget(begCheck)

octave = QtGui.QCheckBox("Octave correction")
optionsLayout.addWidget(octave)

####

otherGroup = QtGui.QGroupBox("Other")
otherLayout = QtGui.QGridLayout()
otherGroup.setLayout(otherLayout)

playWav = QtGui.QPushButton("Play WAV File", enabled=False)
otherLayout.addWidget(playWav)

playMidi = QtGui.QPushButton("Play MIDI File", enabled=False)
otherLayout.addWidget(playMidi)

matplotlib = QtGui.QPushButton("Draw with Matplotlib", enabled=False)
otherLayout.addWidget(matplotlib)

####

buttons.addWidget(generalGroup, row=0, col=0)
buttons.addWidget(thresholdGroup, row=0, col=3)
buttons.addWidget(paramGroup, row=0, col=2)
buttons.addWidget(optionsGroup, row=0, col=4)
buttons.addWidget(otherGroup, row=0, col=5)

file_path = None

def fileSelected():

    progressBar.setFormat(file_path)        
    paramGroup.setEnabled(True)
    analyze.setEnabled(True)
    thresholdGroup.setEnabled(False)
    optionsGroup.setEnabled(False)
    midi.setEnabled(False)
    begCheck.setCheckState(0)
    playWav.setEnabled(True)
    playMidi.setEnabled(False)
    matplotlib.setEnabled(False)

    p1.clear()
    p2.clear()
    p3.clear()
    p4.clear()

def browseClick(self):

    file_dialog = QtGui.QFileDialog()
    file_dialog.setNameFilters(["Wav files (*.wav)"])
    file_dialog.selectNameFilter("Wav files (*.wav)")

    if file_dialog.exec_():
        global file_path
        file_path = file_dialog.selectedFiles()[0]
        fileSelected()
        

browse.clicked.connect(browseClick)

graphs = None
pointerList = None

half_h = 5
c = 1.05
onsets = []

def analyzeButton():

    buttons.setEnabled(False)
    progressBar.setEnabled(True)
    progressBar.setMaximum(8)

    import subprocess
    proc = subprocess.Popen(["python", "analyze.py", "-f", file_path, 
                            "-w", str(window.value()), "-p", str(highpass.value()),
                            "-r", str(hps.value()), "-i"], stdout=subprocess.PIPE)

    i = 0
    while proc.poll() is None:

        l = proc.stdout.readline() # This blocks until it receives a newline.
         
        if l != b'':

            progressBar.setFormat(l.decode('UTF-8'))
            progressBar.setValue(i)
            i += 1
            app.processEvents()

    global graphs
    global pointerList

    import pickle
    with open('results.temp','rb') as f:

        graphs = pickle.load(f)
        drawResults()

    os.remove('results.temp')

    begCheck.setCheckState(0)
    matplotlib.setEnabled(True)

analyze.clicked.connect(analyzeButton)

def drawResults():

    global half_h, c, onsets

    frequencies = graphs[4]

    maxf = np.amax(frequencies)
    minf = np.amin([i for i in frequencies if i != 0])

    spectrogram1 = pg.ImageItem(border='w')
    spectrogram1.setImage(graphs[3])
    p1.addItem(spectrogram1)

    p1.plot(frequencies, pen=pg.mkPen('k', width=2))
    p1.setYRange(minf - 10 if minf>10 else 0, maxf+10)

    spectrogram2 = pg.ImageItem(border='w')
    spectrogram2.setImage(graphs[0])
    p3.addItem(spectrogram2)
    p3.setTitle("Narrowband Spectrogram (Window Size: " + str(2**window.value()) +")")

    spectrogram3 = pg.ImageItem(border='w')
    spectrogram3.setImage(graphs[1])
    p4.addItem(spectrogram3)
    p4.setTitle("Wideband Spectrogram (Window Size: 44100)")

    updateThreshold()

    buttons.setEnabled(True)
    thresholdGroup.setEnabled(True)
    optionsGroup.setEnabled(True)
    midi.setEnabled(True)

    app.processEvents()

def updateThreshold():

    p2.clear()
    
    detection = graphs[5]
    (peaks, threshold) = iu.peaks(detection, half_h, c)

    p2.plot(detection, pen=pg.mkPen('c', width=2), name="Detection function")
    p2.plot(threshold, pen=pg.mkPen('r', width=2), name="Dynamic Threshold")

    for p in peaks:
        p2.addItem(pg.InfiniteLine(p, pen=pg.mkPen('w', width=1)))

    global onsets
    onsets = [ i / len(detection) for i in peaks ]

def upButton():
    global c
    c += 0.01
    cLabel.setText('c = ' + str(c))
    updateThreshold()

def downButton():
    global c
    c  -= 0.01
    cLabel.setText('c = ' + str(c))    
    updateThreshold()

def flatButton():
    global half_h
    half_h += 1
    hLabel.setText('h = ' + str(half_h))    
    updateThreshold()

def steepButton():
    global half_h
    if half_h > 1:
        half_h -= 1
    hLabel.setText('h = ' + str(half_h))   
    updateThreshold()

up.clicked.connect(upButton)
down.clicked.connect(downButton)
flat.clicked.connect(flatButton)
steep.clicked.connect(steepButton)

midi_file = None

def midiButton():

    from ctypes import cdll, c_void_p, c_double, c_uint, cast, c_char_p

    mylib = cdll.LoadLibrary('target\debug\wav2midi.dll')

    (frequencies, detection) = (graphs[4],  graphs[5])
    (peaks, threshold) = iu.peaks(detection, half_h, c)

    if octave.isChecked():

        frequencies = iu.octave_correction(frequencies, graphs[1])
        graphs[4] = frequencies
        p1.plot(frequencies, pen=pg.mkPen('r', width=2))
        maxf = np.amax(frequencies)
        minf = np.amin([i for i in frequencies if i != 0])
        p1.setYRange(minf - 10 if minf>10 else 0, maxf+10)
        app.processEvents()
    
    global midi_file
    mylib.create_midi.restype = c_char_p
    midi_file = mylib.create_midi((c_uint * len(frequencies))(*frequencies), len(frequencies),
                                  (c_double * len(onsets))(*onsets), len(onsets),
                                   file_path.encode('UTF-8'), not onsetCheck.isChecked())

    base = os.path.basename(midi_file.decode('UTF-8'))
    midi_file = os.path.splitext(base)[0] + ".mid"
    os.startfile(midi_file)

    playMidi.setEnabled(True)

midi.clicked.connect(midiButton)

def onsetCheckButton():
    
    if onsetCheck.isChecked():

        begCheck.setEnabled(True)
        updateThreshold()
        thresholdGroup.setEnabled(True)

    else:

        begCheck.setEnabled(False)
        begCheck.setCheckState(0)
        thresholdGroup.setEnabled(False)        

        if len(save) != 0:

            graphs[4] = save
            drawResults()

        p2.clear()

        detection = graphs[5]
        (peaks, threshold) = iu.peaks(detection, half_h, c)
       
        detection = graphs[5]
        (peaks, threshold) = iu.peaks(detection, half_h, c)
        p2.plot(detection, pen=pg.mkPen('c', width=2), name="Detection function")
        p2.plot(threshold, pen=pg.mkPen('r', width=2), name="Dynamic Threshold")


onsetCheck.clicked.connect(onsetCheckButton)

save = []
def begCheckButton():

    end = int(len(graphs[4])*onsets[0])
    global save
    
    if begCheck.isChecked():
    
        save = list(graphs[4])
        
        for i in range(0, end):
            graphs[4][i] = 0

    else:

        graphs[4] = save

    drawResults()


begCheck.clicked.connect(begCheckButton)

def matplotlibButton():

    (frequencies, detection) = (graphs[4],  graphs[5])
    (peaks, threshold) = iu.peaks(detection, half_h, c)
    exec(open('spectrogram.py').read(), globals(), locals())

matplotlib.clicked.connect(matplotlibButton)

def playWavButton():
    os.startfile(file_path)

playWav.clicked.connect(playWavButton)

def playMidiButton():
    os.startfile(midi_file)

playMidi.clicked.connect(playMidiButton) 

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()