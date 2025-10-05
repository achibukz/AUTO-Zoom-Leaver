#!/bin/bash

# Zoom Auto Leaver - macOS App Build Script
# Creates a native macOS .app bundle using PyInstaller

echo "🍎 Building Zoom Auto Leaver.app"
echo "================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create/activate virtual environment
if [ ! -d "venv_build" ]; then
    echo "📦 Creating build environment..."
    python3 -m venv venv_build
fi

source venv_build/bin/activate

# Install build dependencies
echo "📥 Installing build dependencies..."
pip install --upgrade pip
pip install pyinstaller
pip install pyinstaller
pip install -r requirements_macos.txt

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist __pycache__
rm -f *.spec.bak

# Build the app
echo "🔨 Building application..."
pyinstaller zoom_auto_leaver_macos.spec

# Check if build was successful
if [ -d "dist/Zoom Auto Leaver.app" ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📱 Your app is ready: dist/Zoom Auto Leaver.app"
    echo ""
    echo "To install and use:"
    echo "1. Drag 'Zoom Auto Leaver.app' to your Applications folder"
    echo "2. Right-click and select 'Open' the first time (macOS security)"
    echo "3. Grant Accessibility permissions when prompted:"
    echo "   System Preferences > Security & Privacy > Privacy > Accessibility"
    echo "4. Launch from Applications or Spotlight search"
    echo ""
    echo "🎉 Installation complete!"
    
    # Optionally open the dist folder
    read -p "Open dist folder in Finder? (y/N): " open_finder
    if [[ $open_finder =~ ^[Yy]$ ]]; then
        open dist/
    fi
    
else
    echo "❌ Build failed!"
    echo "Check the output above for errors."
    exit 1
fi

# Cleanup option
echo ""
read -p "🧹 Clean up build files? (y/N): " cleanup
if [[ $cleanup =~ ^[Yy]$ ]]; then
    rm -rf build __pycache__
    echo "✅ Cleanup completed"
fi

deactivate