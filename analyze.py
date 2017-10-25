from ctypes import cdll
from sys import argv
import time
import os

start_time = time.time()

stft_rs = cdll.LoadLibrary('target\debug\stft_rust.dll')

if len(argv) == 2:
    stft_rs.analyze(argv[1].encode('UTF-8'), False)
    print("Finished in %s seconds" % int(time.time() - start_time))

elif len(argv) == 3 and argv[2] == '--draw':
    os.system('spectrogram.py ' + argv[1])

else:
    print ('Correct usage: analyze.py <file_name> [--draw]')