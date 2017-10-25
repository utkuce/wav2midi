all: rust_lib python_reqs
	pyinstaller --add-binary "target/debug/stft_rust.dll;." analyze.py --onefile

rust_lib:
	cargo build

python_reqs:
	pip install matplotlib
	pip install numpy
	pip install pyinstaller
