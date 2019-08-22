SINGLE_FILE = 0

COMMAND := pyinstaller --add-binary "target/debug/wav2midi.dll;." analyze.py --hidden-import matplotlib

ifeq ($(SINGLE_FILE), 1)
COMMAND += --onefile
endif

all: rust_lib python_reqs
	$(COMMAND)	

rust_lib:
	cargo +nightly build

python_reqs:
	pip install matplotlib
	pip install numpy
	pip install pyinstaller
	pip install PyQt5 
	pip install pyqtgraph