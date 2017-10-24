from ctypes import cdll
from sys import argv
import time

start_time = time.time()

stft_rs = cdll.LoadLibrary('target\debug\stft_rust.dll')
stft_rs.analyze(argv[1].encode('UTF-8'))

print("Finished in %s seconds" % int(time.time() - start_time))
