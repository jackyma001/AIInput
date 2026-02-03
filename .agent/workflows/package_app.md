---
description: How to package the AIInput assistant into a standalone EXE file
---
# Package AIInput as an EXE

This workflow will package your Python application into a single executable file, making it easy to run without opening a terminal.

1. Install PyInstaller (if not already installed)
// turbo
```powershell
pip install pyinstaller
```

2. Package the application
// turbo
```powershell
pyinstaller --noconfirm --onefile --windowed --icon="D:/github/AIInput/assets/icon.ico" --name="AIInput" --add-data="src;src" --add-data=".env;." "D:/github/AIInput/src/main.py"
```

3. Locate the EXE
The executable will be in the `dist` folder: `d:\github\AIInput\dist\AIInput.exe`.

4. Create a Shortcut (Optional)
Right-click `AIInput.exe` -> "Send to" -> "Desktop (create shortcut)".
