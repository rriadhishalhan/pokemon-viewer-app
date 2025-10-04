@echo off
echo Pokemon Viewer Web Application
echo ================================

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

echo.
echo Installing/Updating requirements...
C:/Users/rezky/Documents/REPO/test-copilot/.venv/Scripts/pip.exe install -r requirements.txt

echo.
echo Starting Pokemon Viewer Web Application...
echo.
echo Open your browser and navigate to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

C:/Users/rezky/Documents/REPO/test-copilot/.venv/Scripts/python.exe web_app.py

pause