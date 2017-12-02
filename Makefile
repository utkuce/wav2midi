SINGLE_FILE = 0

COMMAND := pyinstaller --add-binary "target/debug/mylib.dll;." analyze.py

ifeq ($(SINGLE_FILE), 1)
COMMAND += --onefile
endif

all: rust_lib python_reqs
	$(COMMAND)	

rust_lib:
	cargo build

python_reqs:
	pip install matplotlib
	pip install numpy
	pip install pyinstaller
