# AUTO Zoom Leaver

A Python application that automatically leaves Zoom meetings when the participant count drops below a configurable threshold.

## How It Works

The application monitors Zoom window titles to detect the participant count and automatically leaves the meeting when:
1. **Detects participant count** from Zoom window titles (e.g., "Participants (5)")
2. **Checks threshold** - compares current count with your configured threshold  
3. **Leaves meeting** - executes the sequence: Focus → Alt+Q → Enter

## Features

- **Simple Detection** - Uses window titles instead of complex OCR
- **Configurable Threshold** - Set your minimum participant count
- **Automatic Leave Sequence** - Focus window → Alt+Q → Enter  
- **Multiple Window Support** - Works with different Zoom window types
- **Interactive Configuration** - Easy setup through console menu
- **Background Monitoring** - Runs continuously in the background

## Quick Start

1. **Install Python** (3.7 or higher)

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python zoom_auto_leaver.py
   ```

4. **Configure Settings** (choose option 2):
   - Set participant threshold (default: 5)
   - Set check interval (default: 10 seconds)
   - Enable/disable logging

5. **Start Monitoring** (choose option 1):
   - Application will monitor Zoom windows
   - Automatically leaves when threshold is reached

2. Configure your settings:
   - **Participant Threshold**: Number of participants below which you want to leave (default: 2)
   - **Check Interval**: How often to check participant count in seconds (default: 5)
   - **Debug Mode**: Enable to save screenshots for troubleshooting

3. Click "Start Monitoring" to begin
## Configuration Options

- **Participant Threshold**: Minimum number of participants to stay in meeting
- **Check Interval**: How often to check participant count (seconds)
- **Auto-start**: Automatically start monitoring on launch
- **Logging**: Enable/disable activity logging

## Requirements

- Python 3.7+
- Windows (primary support)
- Active Zoom meeting with visible participant count

## Dependencies

- `pygetwindow` - Window detection and management
- `pyautogui` - Keyboard automation

## How to Use

### Menu Options:

1. **Start Monitoring** - Begin watching for participant count
2. **Configure Settings** - Adjust threshold and other options  
3. **Test Detection** - Check if Zoom windows are detected properly
4. **Exit** - Quit the application

### Window Detection:

The app looks for Zoom windows and tries to find participant count in titles like:
- "Participants (15)"
- "15 participants" 
- "Meeting - Participants: 10"

### Leave Sequence:

When threshold is reached:
1. Focus on Zoom window
2. Press Alt+Q (Leave Meeting shortcut)
3. Press Enter (Confirm leaving)

## Troubleshooting

### "No Zoom windows found"
- Make sure Zoom is running and visible
- Check that window titles contain "zoom" 
- Try joining a meeting first

### "Could not determine participant count"
- Participant count might not be in window title
- Try opening the Participants panel in Zoom
- Some Zoom versions show count differently

### Leave sequence not working
- Make sure Alt+Q shortcut is enabled in Zoom settings
- Check that Zoom window can receive focus
- Try manually testing Alt+Q in Zoom

## Customization

Edit `config.json` to customize:
```json
{
    "participant_threshold": 5,
    "check_interval": 10,
    "auto_start": false,
    "log_activity": true
}
```

## License

This project is provided as-is for educational purposes.

## Disclaimer

This tool automates keyboard interactions with Zoom. Use responsibly and in accordance with your organization's policies.
