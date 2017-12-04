from ctypes import cdll, c_void_p, c_double, c_uint, cast
import argparse
import time
import internal_utility as iu

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
    required=False, default=1.05, type=float)

parser.add_argument('-i', '--from-interface',
    help='flag to determine if the script is called from the interface',
    action='store_true')

parser.add_argument('-n', '--no-onsets',
    help='flag to use onset detection or not', action='store_true')

args = vars(parser.parse_args())

start_time = time.time()

mylib = cdll.LoadLibrary('target\debug\mylib.dll')
mylib.analyze.restype = c_void_p

results = mylib.analyze(args['file_name'].encode('UTF-8'), args['window'], 
                        args['highpass'], args['hps_rate'])

graphs = iu.from_ffi(results)  


if not args['from_interface']:

    (frequencies, detection) = (graphs[4],  graphs[5])

    (peaks, threshold) = iu.peaks(detection, args['onset_window'], args['threshold_constant'])
    onsets = [ i / len(detection) for i in peaks ]

    print("Finished in %s seconds" % int(time.time() - start_time))    

    mylib.create_midi((c_uint * len(frequencies))(*frequencies), len(frequencies),
                    (c_double * len(onsets))(*onsets), len(onsets),
                    args['file_name'].encode('UTF-8'), args['no_onsets'])

    exec(open('spectrogram.py').read(), globals(), locals())

else:

    import pickle
    with open('results.temp', 'wb') as f:
        pickle.dump( graphs, f )

mylib.clean2d.argtypes = [c_void_p]
mylib.clean1d.argtypes = [c_void_p]

for i,g in enumerate(iu.pointerList.pointers):
    ptr = cast(g, c_void_p)
    mylib.clean2d(ptr) if i < 4 else mylib.clean1d(ptr)                             