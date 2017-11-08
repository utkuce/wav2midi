from ctypes import cdll, c_void_p
from sys import argv
import time
import spectrogram

start_time = time.time()

mylib = cdll.LoadLibrary('target\debug\mylib.dll')
mylib.analyze.restype = c_void_p

draw = len(argv) == 4 and argv[3] == '--draw'

if not draw and len(argv) != 3:
    print ('Correct usage: analyze.py <file_name> <hps_rate> [--draw]')
else:
    results = mylib.analyze(argv[1].encode('UTF-8'), int(argv[2]), draw)
    print("Finished in %s seconds" % int(time.time() - start_time))    
    if draw:
        spectrogram.draw(results, mylib)