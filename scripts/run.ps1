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

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import pyautogui, pytesseract, PIL, psutil" 2>$null
    Write-Host "All dependencies are installed" -ForegroundColor Green
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check for Tesseract OCR
Write-Host "Checking for Tesseract OCR..." -ForegroundColor Yellow
$tesseractPaths = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
)

$tesseractFound = $false
foreach ($path in $tesseractPaths) {
    if (Test-Path $path) {
        Write-Host "Found Tesseract at: $path" -ForegroundColor Green
        $tesseractFound = $true
        break
    }
}

if (-not $tesseractFound) {
    Write-Host "WARNING: Tesseract OCR not found in standard locations" -ForegroundColor Yellow
    Write-Host "Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Yellow
    Write-Host "The application may not work correctly without it." -ForegroundColor Yellow
    Write-Host ""
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
