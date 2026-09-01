# AUTO Zoom Leaver - PowerShell Launcher
Write-Host "Starting AUTO Zoom Leaver..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if the runtime packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
python -c "import psutil, pyautogui; from pywinauto import Desktop" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "All dependencies are installed" -ForegroundColor Green
} else {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    python -m pip install -r requirements_windows.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Run the application
Write-Host "Starting application..." -ForegroundColor Green
Write-Host ""

try {
    python zoom_auto_leaver.py
} catch {
    Write-Host ""
    Write-Host "Application encountered an error." -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
