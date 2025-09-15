import pygetwindow as gw
import pyautogui
import time
import re
import json
import os
from datetime import datetime

class ZoomAutoLeaver:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.load_config()
        self.running = False
    
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "participant_threshold": 5,
            "check_interval": 10,  # seconds
            "auto_start": False,
            "log_activity": True
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    self.config = {**default_config, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save current configuration to JSON file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def log(self, message):
        """Log activity if enabled"""
        if self.config.get("log_activity", True):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def find_zoom_windows(self):
        """Find all Zoom-related windows"""
        windows = gw.getAllWindows()
        zoom_windows = []
        
        for window in windows:
            if window.title:
                title_lower = window.title.lower()
                # Include Zoom windows AND participant windows
                if ('zoom' in title_lower or 'participant' in title_lower):
                    # Skip certain types of windows but be more specific
                    if any(skip in title_lower for skip in ['installer', 'update', 'uninstall', 'visual studio code']):
                        continue
                    zoom_windows.append(window)
        
        return zoom_windows
    
    def get_participant_count_from_windows(self):
        """Extract participant count from any Zoom window title"""
        try:
            zoom_windows = self.find_zoom_windows()
            
            if not zoom_windows:
                return None
            
            # Prioritize the Participants window first
            participant_windows = [w for w in zoom_windows if 'participant' in w.title.lower()]
            other_windows = [w for w in zoom_windows if 'participant' not in w.title.lower()]
            
            # Check participant windows first, then other zoom windows
            for window in participant_windows + other_windows:
                title = window.title
                self.log(f"Checking window: {title}")
                
                # Look for various patterns that might contain participant count
                patterns = [
                    r'participants?\s*\((\d+)\)',  # "Participants (15)"
                    r'participants?\s*:\s*(\d+)',  # "Participants: 15"
                    r'participants?\s+(\d+)',      # "Participants 15"
                    r'\((\d+)\)\s*participants?',  # "(15) Participants"
                    r'(\d+)\s+participants?',      # "15 participants"
                    r'meeting\s+id.*?\((\d+)\)',   # Meeting with participant count
                    r'\((\d+)\)',                  # Any number in parentheses (as fallback)
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, title, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        # Sanity check - participant count should be reasonable
                        if 1 <= count <= 10000:  # Reasonable range
                            self.log(f"Found participant count: {count} in window: {title}")
                            return count
            
            return None
            
        except Exception as e:
            self.log(f"Error getting participant count: {e}")
            return None
    
    def find_main_zoom_window(self):
        """Find the main Zoom meeting window for focusing"""
        zoom_windows = self.find_zoom_windows()
        
        if not zoom_windows:
            return None
        
        # Prefer windows that look like main meeting windows
        priority_keywords = ['meeting', 'zoom meeting', 'participants']
        
        for window in zoom_windows:
            title_lower = window.title.lower()
            if any(keyword in title_lower for keyword in priority_keywords):
                return window
        
        # Return the first available zoom window
        return zoom_windows[0] if zoom_windows else None
    
    def leave_zoom_meeting(self):
        """Execute the sequence to leave Zoom meeting"""
        try:
            zoom_window = self.find_main_zoom_window()
            if not zoom_window:
                self.log("No Zoom window found to focus on!")
                return False
            
            self.log(f"Leaving Zoom meeting... Focusing on: {zoom_window.title}")
            
            # Step 1: Focus to Zoom
            zoom_window.activate()
            time.sleep(1)  # Give time for window to focus
            
            # Step 2: Press Alt+Q (Leave Meeting shortcut)
            pyautogui.hotkey('alt', 'q')
            time.sleep(0.5)  # Give time for dialog to appear
            
            # Step 3: Press Enter (Confirm leaving)
            pyautogui.press('enter')
            
            self.log("Successfully executed leave meeting sequence!")
            return True
            
        except Exception as e:
            self.log(f"Error leaving meeting: {e}")
            return False
    
    def monitor_meeting(self):
        """Main monitoring loop"""
        self.running = True
        self.log(f"Starting Zoom Auto Leaver...")
        self.log(f"Participant threshold: {self.config['participant_threshold']}")
        self.log(f"Check interval: {self.config['check_interval']} seconds")
        self.log("Looking for participant count in Zoom window titles...")
        
        try:
            while self.running:
                participant_count = self.get_participant_count_from_windows()
                
                if participant_count is not None:
                    self.log(f"Current participants: {participant_count}")
                    
                    if participant_count <= self.config['participant_threshold']:
                        self.log(f"Participant count ({participant_count}) reached threshold ({self.config['participant_threshold']})")
                        if self.leave_zoom_meeting():
                            self.log("Meeting left successfully. Stopping monitor.")
                            break
                        else:
                            self.log("Failed to leave meeting. Will try again.")
                else:
                    zoom_windows = self.find_zoom_windows()
                    if zoom_windows:
                        self.log(f"Found {len(zoom_windows)} Zoom window(s) but could not determine participant count")
                        for i, window in enumerate(zoom_windows):
                            self.log(f"  Window {i+1}: {window.title}")
                    else:
                        self.log("No Zoom windows found. Waiting...")
                
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            self.log("Monitoring stopped by user")
        except Exception as e:
            self.log(f"Error in monitoring loop: {e}")
        finally:
            self.running = False
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.running = False
    
    def configure(self):
        """Interactive configuration"""
        print("\n=== Zoom Auto Leaver Configuration ===")
        print(f"Current threshold: {self.config['participant_threshold']}")
        print(f"Current check interval: {self.config['check_interval']} seconds")
        print(f"Auto-start monitoring: {self.config['auto_start']}")
        print(f"Log activity: {self.config['log_activity']}")
        
        while True:
            print("\nConfiguration options:")
            print("1. Set participant threshold")
            print("2. Set check interval")
            print("3. Toggle auto-start")
            print("4. Toggle logging")
            print("5. Save and return to main menu")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == '1':
                try:
                    threshold = int(input(f"Enter participant threshold (current: {self.config['participant_threshold']}): "))
                    if threshold > 0:
                        self.config['participant_threshold'] = threshold
                        print(f"Threshold set to {threshold}")
                    else:
                        print("Threshold must be greater than 0")
                except ValueError:
                    print("Please enter a valid number")
            
            elif choice == '2':
                try:
                    interval = int(input(f"Enter check interval in seconds (current: {self.config['check_interval']}): "))
                    if interval > 0:
                        self.config['check_interval'] = interval
                        print(f"Check interval set to {interval} seconds")
                    else:
                        print("Interval must be greater than 0")
                except ValueError:
                    print("Please enter a valid number")
            
            elif choice == '3':
                self.config['auto_start'] = not self.config['auto_start']
                print(f"Auto-start set to {self.config['auto_start']}")
            
            elif choice == '4':
                self.config['log_activity'] = not self.config['log_activity']
                print(f"Logging set to {self.config['log_activity']}")
            
            elif choice == '5':
                self.save_config()
                print("Configuration saved!")
                break
            
            else:
                print("Invalid choice. Please try again.")

def main():
    auto_leaver = ZoomAutoLeaver()
    
    # Auto-start if configured
    if auto_leaver.config.get('auto_start', False):
        auto_leaver.monitor_meeting()
        return
    
    # Interactive menu
    while True:
        print("\n=== Zoom Auto Leaver ===")
        print("1. Start monitoring")
        print("2. Configure settings")
        print("3. Test Zoom window detection")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            try:
                auto_leaver.monitor_meeting()
            except KeyboardInterrupt:
                print("\nMonitoring stopped.")
        
        elif choice == '2':
            auto_leaver.configure()
        
        elif choice == '3':
            print("Scanning all windows...")
            all_windows = gw.getAllWindows()
            relevant_windows = [w for w in all_windows if w.title and ('zoom' in w.title.lower() or 'participant' in w.title.lower())]
            
            print(f"Found {len(relevant_windows)} potentially relevant window(s):")
            for i, window in enumerate(relevant_windows):
                print(f"  {i+1}. '{window.title}'")
            
            zoom_windows = auto_leaver.find_zoom_windows()
            print(f"\nAfter filtering, found {len(zoom_windows)} Zoom window(s):")
            for i, window in enumerate(zoom_windows):
                print(f"  {i+1}. '{window.title}'")
            
            participant_count = auto_leaver.get_participant_count_from_windows()
            if participant_count is not None:
                print(f"\nCurrent participant count: {participant_count}")
            else:
                print("\nCould not determine participant count from window titles")
        
        elif choice == '4':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
