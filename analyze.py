from ctypes import cdll, c_void_p
import argparse
import time
import spectrogram

parser = argparse.ArgumentParser(description='Converts a monophonic wav file into MIDI')

parser.add_argument('-f', '--file-name',
    help='The file that is to be analyzed',
    required=True, type=str)

parser.add_argument('-w','--window', 
    help='2 raised to the w will be used as window length for narrowband spectrogram', 
    required=False, default=13, type=int)

parser.add_argument('-p', '--highpass', 
    help='highpass filter frequency for preprocessing',
    required=False, default=30, type=int)

parser.add_argument('-r', '--hps-rate', 
    help='the rate used for harmonic product spectrum',
    required=False, default=3, type=int)

parser.add_argument('-o', '--onset-window',
    help='half the length of the sliding window used for onset detection thresholding',
    required=False, default=5, type=int)

parser.add_argument('-c', '--threshold-constant',
    help='constant value for scaling the threshold for onset detection',
    required=False, default=1, type=float)

args = vars(parser.parse_args())

start_time = time.time()

mylib = cdll.LoadLibrary('target\debug\mylib.dll')
mylib.analyze.restype = c_void_p

results = mylib.analyze(args['file_name'].encode('UTF-8'), args['window'], args['highpass'], args['hps_rate'])
print("Finished in %s seconds" % int(time.time() - start_time))    
spectrogram.draw(results, mylib, args['onset_window'], args['threshold_constant'])