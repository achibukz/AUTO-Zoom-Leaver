# AUTO Zoom Leaver

Automatically leaves Zoom meetings when the participant count drops below a configured threshold.

## 🚀 Quick Start

### Windows
```bash
python zoom_auto_leaver.py
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
├── config.json                 # Configuration file
├── requirements*.txt           # Dependencies
├── docs/                       # Documentation
│   ├── README_macOS.md        # macOS-specific guide
│   └── BUILD_INSTRUCTIONS.md  # App building guide
├── tools/                      # Build and utility scripts
│   ├── build_macos_app.sh     # macOS app builder
│   ├── run_macos.sh           # macOS setup script
│   ├── create_icon.py         # Icon generator
│   └── *.spec                 # PyInstaller configs
└── scripts/                   # Platform-specific runners
    ├── run.bat               # Windows batch file
    ├── run.ps1               # PowerShell script
    └── cmd.exe               # Windows executable
```

## ✨ Features

- **Cross-Platform**: Native Windows and macOS versions
- **Smart Detection**: Monitors participant count via window titles  
- **Configurable**: Customizable thresholds and intervals
- **Native Apps**: Build standalone `.app` bundles for macOS
- **Auto-Leave**: Executes platform-specific quit sequences
- **Logging**: Detailed activity tracking

## 🔧 Installation

### Basic Setup
```bash
git clone https://github.com/achibukz/AUTO-Zoom-Leaver.git
cd AUTO-Zoom-Leaver
pip install -r requirements.txt  # Windows
pip install -r requirements_macos.txt  # macOS
```

### macOS App (Recommended)
```bash
./tools/build_macos_app.sh
# Drag resulting .app to Applications folder
```

## ⚙️ Configuration

Edit `config.json` or use the interactive menu:

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

1. **Detection**: Scans for Zoom windows with participant info
2. **Monitoring**: Checks participant count every X seconds  
3. **Trigger**: When count ≤ threshold, initiates leave sequence
4. **Exit**: Platform-specific quit command + confirmation

## 📱 Platform Differences

| Feature | Windows | macOS |
|---------|---------|-------|
| Shortcut | `Alt+Q` | `Cmd+Q` |
| Window Detection | pygetwindow | AppKit/AppleScript |
| Native App | ❌ | ✅ (.app bundle) |
| Menu Bar | ❌ | ✅ (planned) |

## 🛠️ Development

### Build Tools
- `tools/build_macos_app.sh` - Create macOS application
- `tools/run_macos.sh` - Development setup script
- `tools/create_icon.py` - Generate app icons

### Documentation  
- `docs/README_macOS.md` - macOS-specific documentation
- `docs/BUILD_INSTRUCTIONS.md` - Detailed build guide

## ⚠️ Important Notes

- **Test First**: Always test in non-important meetings
- **Permissions**: macOS requires Accessibility permissions
- **Backup Plan**: Have manual exit strategies ready
- **Responsibility**: Use at your own risk

## 📖 Platform-Specific Guides

- **macOS Users**: See `docs/README_macOS.md`  
- **Building Apps**: See `docs/BUILD_INSTRUCTIONS.md`
- **Windows Users**: Use `zoom_auto_leaver.py` directly
- **Windows diagnostic**: See `docs/WINDOWS_DIAGNOSTIC.md` for the read-only UI Automation probe

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test on your platform
4. Submit pull request

## 📄 License

Use responsibly and at your own risk. Not liable for unintended meeting departures.
