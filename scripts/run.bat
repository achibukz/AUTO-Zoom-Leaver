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

REM Check if the runtime packages are installed
echo Checking dependencies...
python -c "import psutil, pyautogui; from pywinauto import Desktop" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    python -m pip install -r requirements_windows.txt
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
