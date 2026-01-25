import PyInstaller.__main__
import os
import sys

# Get the absolute path of the project directory
project_dir = os.path.dirname(os.path.abspath(__file__))

# Define path to main script
main_script = os.path.join(project_dir, 'src', 'main.py')

# PyInstaller arguments
args = [
    main_script,
    '--name=AIInput',
    '--onefile',            # Bundle into a single executable
    '--windowed',           # No console window
    '--collect-all=faster_whisper',
    '--collect-all=ctranslate2',
    '--collect-all=pynput',
    '--collect-all=PyQt5',
    '--collect-all=tokenizers',
    '--collect-all=huggingface_hub',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=ctranslate2',
    '--hidden-import=faster_whisper',
    '--hidden-import=onnxruntime',
    '--hidden-import=pynput.keyboard._win32',
    '--hidden-import=pynput.mouse._win32',
    '--hidden-import=requests',
    '--hidden-import=pyaudio',
    '--hidden-import=charset_normalizer',
    '--hidden-import=idna',
    '--hidden-import=urllib3',
    '--add-data=src;src',   # Include the src folder
    '--clean',
]

print(f"Building AIInput EXE...")
PyInstaller.__main__.run(args)
print(f"Build complete! Check the 'dist' folder.")
