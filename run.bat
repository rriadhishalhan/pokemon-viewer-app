@echo off
echo Pokemon Viewer Setup and Launch
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
echo Installing requirements...
pip install -r requirements.txt

echo.
echo Running demo test...
python demo.py

echo.
echo Starting Pokemon Viewer...
python main.py

pause