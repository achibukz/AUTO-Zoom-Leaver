#!/bin/bash

# Zoom Auto Leaver - macOS Run Script
# This script sets up and runs the macOS version of Zoom Auto Leaver

echo "🍎 Zoom Auto Leaver - macOS Version"
echo "===================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 from https://www.python.org/ or using Homebrew:"
    echo "brew install python"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not found."
    echo "Please install pip or reinstall Python 3."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv_macos" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv_macos
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv_macos/bin/activate

# Install/upgrade requirements
echo "📥 Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements_macos.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    echo "You may need to install Xcode command line tools:"
    echo "xcode-select --install"
    exit 1
fi

# Check permissions
echo "🔒 Checking macOS permissions..."
echo "Note: You may need to grant Terminal (or Python) Accessibility permissions"
echo "Go to: System Preferences > Security & Privacy > Privacy > Accessibility"
echo "Add Terminal and/or Python to the allowed applications list."
echo ""

# Run the program
echo "🚀 Starting Zoom Auto Leaver (macOS)..."
python3 zoom_auto_leaver_macos.py

# Deactivate virtual environment when done
deactivate