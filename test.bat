@echo off
if %~1==1 ( analyze.py -f testaudio/tetris2.wav -w 13 -p 215 -r 3 -o 8 -c 1.03 )
if %~1==2 ( analyze.py -f testaudio/tetris_violin.wav -w 13 -p 215 -r 6 -o 7 -c 1.02 )