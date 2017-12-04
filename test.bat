@echo off
if %~1==1 ( analyze.py -f testaudio/tetris2.wav -w 13 -p 215 -r 3 -o 7 -c 1.03 )
if %~1==2 ( analyze.py -f testaudio/tetris_violin.wav -w 13 -p 215 -r 6 -o 7 -c 1.02 )
if %~1==3 ( analyze.py -f testaudio/piano2.wav -c 1.05 -w 12 )
if %~1==4 ( analyze.py -f testaudio/Violin_for_spectrogram.wav -w 12 -o 10 -c 1.02)
if %~1==5 ( analyze.py -f testaudio/mhyst-violin-melody-1.wav -o 4 -c 1.03)
if %~1==6 ( analyze.py -f testaudio/mhyst-violin-hip-hop-riff.wav -c 1.03)
if %~1==7 ( analyze.py -f testaudio/mhyst-violin-melody-5.wav -o 8 -c 1.05)
if %~1==8 ( analyze.py -f testaudio/schuhkarton-1-800-violin.wav -r 6 -w 12 -n)
