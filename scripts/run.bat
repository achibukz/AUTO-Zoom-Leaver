@echo off
echo Starting AUTO Zoom Leaver...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import pyautogui, pytesseract, PIL, psutil" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Run the application
echo Starting application...
python zoom_auto_leaver.py

if errorlevel 1 (
    echo.
    echo Application encountered an error.
    pause
)
