# Building macOS App Bundle

This guide shows how to convert the Zoom Auto Leaver Python script into a native macOS `.app` bundle using PyInstaller.

## Quick Build

**Option 1: Use the build script (recommended)**
```bash
./build_macos_app.sh
```

**Option 2: Manual build**
```bash
# Install build dependencies
pip install -r requirements_build.txt

# Build the app
pyinstaller zoom_auto_leaver_macos.spec
```

## Detailed Steps

### 1. Prerequisites

- **macOS 10.12+** (Sierra or later)
- **Python 3.7+**
- **Xcode Command Line Tools** (for compiling native dependencies)
  ```bash
  xcode-select --install
  ```

### 2. Install Dependencies

```bash
# Create build environment
python3 -m venv venv_build
source venv_build/bin/activate

# Install all build requirements
pip install -r requirements_build.txt
```

### 3. Optional: Create Custom Icon

```bash
# Install Pillow for icon creation
pip install pillow

# Run icon creator
python3 create_icon.py
```

### 4. Build the App

```bash
# Clean previous builds
rm -rf build dist __pycache__

# Build using spec file
pyinstaller zoom_auto_leaver_macos.spec
```

### 5. Test the App

```bash
# Test the built app
open "dist/Zoom Auto Leaver.app"
```

## Build Configuration

The build is configured in `zoom_auto_leaver_macos.spec`:

- **App Name**: "Zoom Auto Leaver"
- **Bundle ID**: `com.achibukz.zoomautoleaver`
- **Windowed**: Yes (no terminal window)
- **Single File**: Yes (all dependencies bundled)
- **Permissions**: Includes proper macOS permission descriptions

### Key Features:

- ✅ **Native .app bundle**
- ✅ **No external dependencies** (all bundled)
- ✅ **Proper macOS permissions** handling
- ✅ **Retina display** support
- ✅ **Code signing** ready (add certificate)
- ✅ **Notarization** ready (with Apple ID)

## Installation

Once built, the app can be distributed by:

1. **Drag to Applications** folder
2. **Right-click → Open** (first time only)
3. **Grant Accessibility** permissions when prompted
4. **Launch** from Applications or Spotlight

## Troubleshooting

### Build Errors

**"Module not found" errors:**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements_build.txt
```

**"Permission denied" during build:**
```bash
# Check Xcode tools
xcode-select --install

# Fix permissions
chmod +x build_macos_app.sh
```

### Runtime Errors

**"App is damaged" message:**
- Right-click app → Open (don't double-click)
- Or: `xattr -cr "Zoom Auto Leaver.app"`

**No window appears:**
- Check Console.app for error messages
- Make sure all dependencies are bundled

**Permission errors:**
- Grant Accessibility permissions in System Preferences
- Add the app to Security & Privacy settings

## Advanced Options

### Code Signing (Optional)

To distribute outside Mac App Store:

```bash
# Sign the app (requires Developer ID)
codesign --force --deep --sign "Developer ID Application: Your Name" "dist/Zoom Auto Leaver.app"

# Verify signature
codesign --verify --verbose "dist/Zoom Auto Leaver.app"
```

### Notarization (Optional)

For Gatekeeper compatibility:

```bash
# Create zip for notarization
ditto -c -k --keepParent "dist/Zoom Auto Leaver.app" "ZoomAutoLeaver.zip"

# Submit for notarization (requires Apple ID)
xcrun notarytool submit ZoomAutoLeaver.zip --apple-id your@email.com --team-id TEAMID --password app-password --wait

# Staple notarization
xcrun stapler staple "dist/Zoom Auto Leaver.app"
```

### Custom Build Options

Edit `zoom_auto_leaver_macos.spec` to customize:

- **Icon**: Change `icon=` parameter
- **Bundle ID**: Modify `bundle_identifier`
- **Permissions**: Add/modify Info.plist entries
- **Hidden imports**: Add modules if needed

## File Structure

After building:
```
dist/
└── Zoom Auto Leaver.app/
    ├── Contents/
    │   ├── Info.plist          # App metadata
    │   ├── MacOS/
    │   │   └── Zoom Auto Leaver # Executable
    │   └── Resources/          # Bundled files
    └── ...
```

## Build Script Options

The `build_macos_app.sh` script supports:

- **Clean build**: Removes old build files
- **Automatic setup**: Creates virtual environment
- **Dependency check**: Installs required packages
- **Success verification**: Checks if app was created
- **Optional cleanup**: Removes build artifacts

---

**Note**: The resulting `.app` is a fully self-contained application that can run on any compatible macOS system without requiring Python or additional dependencies to be installed.