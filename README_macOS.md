# Zoom Auto Leaver - macOS Version

A macOS-native version of the Zoom Auto Leaver that automatically exits Zoom meetings when the participant count drops below a configured threshold.

## Features

- **macOS Native**: Uses AppKit and Cocoa frameworks for better macOS integration
- **AppleScript Integration**: Multiple methods for detecting Zoom windows
- **Configurable Thresholds**: Set custom participant count thresholds
- **Keyboard Shortcuts**: Uses macOS-standard shortcuts (Cmd+W by default)
- **Permission Checking**: Automatically checks for required macOS permissions
- **Multiple Detection Methods**: Uses various approaches to find Zoom windows and participant counts

## Requirements

- macOS 10.12+ (Sierra or later)
- Python 3.7+
- Accessibility permissions for Terminal/Python

## Quick Start

1. **Clone or download** this repository
2. **Run the setup script**:
   ```bash
   ./run_macos.sh
   ```
3. **Grant permissions** when prompted (System Preferences > Security & Privacy > Accessibility)
4. **Configure settings** and start monitoring!

## Manual Installation

If you prefer manual installation:

```bash
# Create virtual environment
python3 -m venv venv_macos
source venv_macos/bin/activate

# Install dependencies
pip install -r requirements_macos.txt

# Run the program
python3 zoom_auto_leaver_macos.py
```

## macOS Permissions

This app requires **Accessibility permissions** to:
- Read window titles from other applications
- Send keyboard shortcuts to Zoom
- Activate and control the Zoom application

### Granting Permissions

1. Open **System Preferences**
2. Go to **Security & Privacy**
3. Click the **Privacy** tab
4. Select **Accessibility** from the left sidebar
5. Click the **lock icon** and enter your password
6. Click **+** and add:
   - **Terminal** (if running from Terminal)
   - **Python** (your Python interpreter)
   - Or the specific app you're using to run the script

## Configuration

The program creates a `config.json` file with these options:

```json
{
    "participant_threshold": 5,
    "check_interval": 10,
    "auto_start": false,
    "log_activity": true,
    "leave_shortcut": "cmd+w",
    "confirm_leave": true
}
```

### Configuration Options

- **participant_threshold**: Leave when participants drop to this number or below
- **check_interval**: How often to check (in seconds)
- **auto_start**: Start monitoring immediately when launched
- **log_activity**: Enable/disable activity logging
- **leave_shortcut**: Keyboard shortcut to leave meeting
- **confirm_leave**: Whether to send confirmation keypress after leave command

### Keyboard Shortcuts

Common Zoom shortcuts on macOS:
- `cmd+w` - Close window/Leave meeting (default)
- `cmd+shift+w` - Leave meeting (alternative)
- `alt+q` - Leave meeting (if configured in Zoom)

## How It Works

1. **Window Detection**: Scans for Zoom windows using multiple methods:
   - NSWorkspace API for running applications
   - AppleScript for window enumeration
   - Direct process querying
   
2. **Participant Counting**: Extracts participant count from window titles using regex patterns:
   - "Participants (15)"
   - "15 participants" 
   - "(15) Participants"
   - And more patterns...

3. **Automated Leaving**: When threshold is reached:
   - Activates Zoom application
   - Sends configured keyboard shortcut
   - Confirms the action (if enabled)

## Troubleshooting

### "Permission Denied" or "Accessibility Error"
- Ensure Accessibility permissions are granted (see above)
- Try restarting Terminal after granting permissions

### "No Zoom Windows Found"
- Make sure Zoom is running and you're in a meeting
- Check that window titles contain participant information
- Use "Test Zoom window detection" in the menu

### "Failed to Leave Meeting"
- Verify the keyboard shortcut in Zoom preferences
- Try different shortcuts in configuration
- Check if Zoom dialog requires different confirmation

### "Import Errors"
- Make sure all dependencies are installed: `pip install -r requirements_macos.txt`
- You may need Xcode command line tools: `xcode-select --install`

## Differences from Windows Version

- Uses **Cmd** instead of **Alt** for shortcuts
- Uses **AppKit/Cocoa** instead of **pygetwindow**
- Includes **AppleScript** integration for better macOS compatibility
- Has **permission checking** for macOS security requirements
- Uses **NSWorkspace** for application management

## Testing

Use the built-in test features:
1. **Test Zoom window detection** - See what Zoom windows are found
2. **Test leave sequence** - Try the leave procedure (be careful!)
3. **Check permissions** - Verify macOS permissions are correct

## Security Notes

- This app only reads window titles and sends keyboard shortcuts
- No personal data is collected or transmitted
- All processing happens locally on your machine
- Configuration is stored in a local JSON file

## Contributing

Feel free to submit issues or pull requests! This macOS version can be improved with:
- Better window detection methods
- Additional Zoom shortcut support
- Enhanced error handling
- UI improvements

## License

Same as the original project - use responsibly and at your own risk!

---

**Note**: This is an automated tool that controls your computer. Test it thoroughly before relying on it for important meetings. The authors are not responsible for any unintended meeting departures!