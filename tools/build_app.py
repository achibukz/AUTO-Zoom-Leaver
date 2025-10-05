#!/usr/bin/env python3
"""
Build script for creating macOS .app bundle using PyInstaller
"""

import subprocess
import sys
import os
import shutil

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed")

def create_app_bundle():
    """Create the macOS app bundle"""
    print("🔨 Building macOS app bundle...")
    
    # PyInstaller command for macOS app
    cmd = [
        "pyinstaller",
        "--name", "Zoom Auto Leaver",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
        "--osx-bundle-identifier", "com.achibukz.zoomautoleaver",
        "--icon", "app_icon.icns" if os.path.exists("app_icon.icns") else None,
        "--add-data", "config.json:." if os.path.exists("config.json") else None,
        "--hidden-import", "PyObjC",
        "--hidden-import", "AppKit",
        "--hidden-import", "Cocoa",
        "--hidden-import", "pyautogui",
        "zoom_auto_leaver_macos.py"
    ]
    
    # Remove None values
    cmd = [arg for arg in cmd if arg is not None]
    
    try:
        subprocess.check_call(cmd)
        print("✅ App bundle created successfully!")
        
        # Move the app to a more accessible location
        app_name = "Zoom Auto Leaver.app"
        source_path = f"dist/{app_name}"
        target_path = f"./{app_name}"
        
        if os.path.exists(source_path):
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.move(source_path, target_path)
            print(f"✅ App moved to: {target_path}")
        
        print("\n🎉 Build completed!")
        print(f"Your app is ready: {target_path}")
        print("\nTo install:")
        print(f"1. Drag '{app_name}' to your Applications folder")
        print("2. Grant Accessibility permissions when prompted")
        print("3. Launch from Applications or Spotlight")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def cleanup():
    """Clean up build artifacts"""
    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = ["*.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned up: {dir_name}")

if __name__ == "__main__":
    print("🍎 Zoom Auto Leaver - macOS App Builder")
    print("=" * 40)
    
    check_dependencies()
    
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        cleanup()
        print("✅ Cleanup completed")
        sys.exit(0)
    
    success = create_app_bundle()
    
    if success:
        cleanup_choice = input("\n🧹 Clean up build files? (y/N): ").lower()
        if cleanup_choice == 'y':
            cleanup()