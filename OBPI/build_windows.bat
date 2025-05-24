@echo off
echo Building OBPI for Windows...

REM Using icon.png for the application icon

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Install requirements
pip install -r requirements.txt

REM Build with PyInstaller
pyinstaller obpi_windows.spec

echo Build complete. Executable is in dist\OBPI-Windows.exe
