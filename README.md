# AUTO Zoom Leaver

Automatically leaves Zoom meetings when the participant count drops below a configured threshold.

## Quick start

### Windows

Download the `AutoZoomLeaver-windows` artifact from a successful `Windows
application` GitHub Actions run. Extract the executable and run
`AutoZoomLeaver.exe`. Python is not required. Read the [Windows guide](docs/README_windows.md)
before the first run.

```bash
AutoZoomLeaver.exe --self-test
AutoZoomLeaver.exe
```

### macOS
```bash
python zoom_auto_leaver_macos.py
```

### Build Native App (macOS)
```bash
./tools/build_macos_app.sh
```

## 📁 Project Structure

```
AUTO-Zoom-Leaver/
├── README.md                    # Main documentation
├── zoom_auto_leaver.py         # Windows version
├── zoom_auto_leaver_macos.py   # macOS version  
├── config.json                 # Legacy source-run configuration file
├── requirements*.txt           # Dependencies
├── docs/                       # Documentation
│   ├── README_windows.md      # Windows installation and use
│   ├── README_macOS.md        # macOS-specific guide
│   └── BUILD_INSTRUCTIONS.md  # macOS app building guide
├── tools/                      # Build and utility scripts
│   ├── build_macos_app.sh     # macOS app builder
│   ├── run_macos.sh           # macOS setup script
│   ├── create_icon.py         # Icon generator
│   └── *.spec                 # PyInstaller configs
└── scripts/                   # Platform-specific runners
    ├── run.bat               # Windows batch file
    ├── run.ps1               # PowerShell script
```

## ✨ Features

- **Cross-Platform**: Native Windows and macOS versions
- **Smart Detection**: Reads participant controls through Windows UI Automation
- **Configurable**: Customizable thresholds and intervals
- **Native Apps**: Build standalone `.exe` and `.app` bundles
- **Auto-Leave**: Executes platform-specific quit sequences
- **Logging**: Detailed activity tracking

## 🔧 Installation

### Basic Setup
```bash
git clone https://github.com/achibukz/AUTO-Zoom-Leaver.git
cd AUTO-Zoom-Leaver
python -m pip install -r requirements_windows.txt  # Windows source run
pip install -r requirements_macos.txt  # macOS
```

### macOS App (Recommended)
```bash
./tools/build_macos_app.sh
# Drag resulting .app to Applications folder
```

## ⚙️ Configuration

For a packaged Windows run, use the interactive menu. It stores settings under
`%LOCALAPPDATA%\AutoZoomLeaver`. A source run can edit the legacy `config.json`:

```json
{
    "participant_threshold": 5,
    "check_interval": 10,
    "auto_start": false,
    "log_activity": true,
    "leave_shortcut": "cmd+q"
}
```

## 🎯 How It Works

1. **Detection**: Scans Zoom's UI Automation controls for participant info
2. **Monitoring**: Checks participant count every X seconds  
3. **Trigger**: When count ≤ threshold, initiates leave sequence
4. **Exit**: Platform-specific quit command + confirmation

## 📱 Platform Differences

| Feature | Windows | macOS |
|---------|---------|-------|
| Shortcut | `Alt+Q` | `Cmd+Q` |
| Window Detection | Microsoft UI Automation | AppKit/AppleScript |
| Native App | ✅ (.exe bundle) | ✅ (.app bundle) |
| Menu Bar | ❌ | ✅ (planned) |

## 🛠️ Development

### Build Tools
- `tools/build_macos_app.sh` - Create macOS application
- `tools/run_macos.sh` - Development setup script
- `tools/create_icon.py` - Generate app icons

### Documentation  
- `docs/README_macOS.md` - macOS-specific documentation
- `docs/README_windows.md` - Windows installation and usage
- `docs/BUILD_INSTRUCTIONS.md` - Detailed build guide

## ⚠️ Important Notes

- **Test First**: Always test in non-important meetings
- **Permissions**: macOS requires Accessibility permissions
- **Backup Plan**: Have manual exit strategies ready
- **Responsibility**: Use at your own risk

## 📖 Platform-Specific Guides

- **macOS Users**: See `docs/README_macOS.md`  
- **Building Apps**: See `docs/BUILD_INSTRUCTIONS.md`
- **Windows Users**: See `docs/README_windows.md`
- **Windows diagnostic**: See `docs/WINDOWS_DIAGNOSTIC.md` for the read-only UI Automation probe

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test on your platform
4. Submit pull request

## 📄 License

Use responsibly and at your own risk. Not liable for unintended meeting departures.
