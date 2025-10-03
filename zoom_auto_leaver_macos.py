#!/usr/bin/env python3
"""
Zoom Auto Leaver - macOS Version
Automatically leaves Zoom meetings when participant count drops below threshold.
Uses macOS-specific window management and keyboard shortcuts.
"""

import time
import re
import json
import os
import subprocess
import threading
from datetime import datetime
try:
    from AppKit import (NSWorkspace, NSApplication, NSApp, NSStatusBar, NSMenu, 
                       NSMenuItem, NSImage, NSStatusItem, NSVariableStatusItemLength,
                       NSApplicationActivationPolicyAccessory, NSTerminateNow)
    from Cocoa import (NSRunningApplication, NSApplicationActivateIgnoringOtherApps, 
                      NSObject, objc)
    import pyautogui
except ImportError as e:
    print(f"Required dependencies not installed: {e}")
    print("Please run: pip install pyobjc-framework-Cocoa pyautogui")
    exit(1)

class ZoomAutoLeaverMacOS:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.load_config()
        self.running = False
        self.workspace = NSWorkspace.sharedWorkspace()
        
    def load_config(self):
        """Load configuration from JSON file"""
        default_config = {
            "participant_threshold": 5,
            "check_interval": 10,  # seconds
            "auto_start": False,
            "log_activity": True,
            "leave_shortcut": "cmd+q",  # macOS quit application - more reliable for leaving Zoom
            "confirm_leave": True
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
    
    def get_window_list_via_applescript(self):
        """Get window list using AppleScript for better compatibility"""
        try:
            # AppleScript to get all window titles from all applications
            script = '''
            tell application "System Events"
                set windowList to {}
                repeat with proc in (every process whose background only is false)
                    try
                        repeat with win in (every window of proc)
                            set windowList to windowList & {name of win as string}
                        end repeat
                    end try
                end repeat
                return windowList
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True)
            window_titles = result.stdout.strip().split(', ')
            return [title.strip() for title in window_titles if title.strip()]
        except Exception as e:
            self.log(f"Error getting window list via AppleScript: {e}")
            return []
    
    def find_zoom_windows(self):
        """Find all Zoom-related windows using multiple methods"""
        zoom_windows = []
        
        try:
            # Method 1: Get running applications
            running_apps = self.workspace.runningApplications()
            zoom_apps = []
            
            for app in running_apps:
                if app.localizedName() and 'zoom' in app.localizedName().lower():
                    zoom_apps.append(app)
            
            # Method 2: Get window titles via AppleScript
            all_window_titles = self.get_window_list_via_applescript()
            
            for title in all_window_titles:
                if title and self._is_zoom_window(title):
                    zoom_windows.append({'title': title, 'method': 'applescript'})
            
            # Method 3: Try to get Zoom window titles directly
            zoom_titles = self._get_zoom_window_titles_direct()
            for title in zoom_titles:
                if title not in [w['title'] for w in zoom_windows]:
                    zoom_windows.append({'title': title, 'method': 'direct'})
                    
        except Exception as e:
            self.log(f"Error finding Zoom windows: {e}")
        
        return zoom_windows
    
    def _is_zoom_window(self, title):
        """Check if a window title indicates a Zoom window"""
        title_lower = title.lower()
        zoom_indicators = ['zoom', 'participant', 'meeting']
        skip_indicators = ['installer', 'update', 'uninstall', 'visual studio', 'vscode']
        
        has_zoom_indicator = any(indicator in title_lower for indicator in zoom_indicators)
        has_skip_indicator = any(skip in title_lower for skip in skip_indicators)
        
        return has_zoom_indicator and not has_skip_indicator
    
    def _get_zoom_window_titles_direct(self):
        """Get Zoom window titles using direct AppleScript query"""
        try:
            script = '''
            tell application "System Events"
                set zoomTitles to {}
                try
                    tell process "zoom.us"
                        repeat with win in (every window)
                            set zoomTitles to zoomTitles & {name of win as string}
                        end repeat
                    end tell
                end try
                return zoomTitles
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                titles = result.stdout.strip().split(', ')
                return [title.strip() for title in titles if title.strip()]
        except Exception:
            pass
        
        return []
    
    def get_participant_count_from_windows(self):
        """Extract participant count from Zoom window titles"""
        try:
            zoom_windows = self.find_zoom_windows()
            
            if not zoom_windows:
                return None
            
            # Prioritize participant windows
            participant_windows = [w for w in zoom_windows if 'participant' in w['title'].lower()]
            other_windows = [w for w in zoom_windows if 'participant' not in w['title'].lower()]
            
            # Check participant windows first, then other zoom windows
            for window in participant_windows + other_windows:
                title = window['title']
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
                        if 1 <= count <= 10000:
                            self.log(f"Found participant count: {count} in window: {title}")
                            return count
            
            return None
            
        except Exception as e:
            self.log(f"Error getting participant count: {e}")
            return None
    
    def activate_zoom_meeting_window(self):
        """Activate/focus the main Zoom meeting window (not participants or other windows)"""
        try:
            # Method 1: Try to focus specifically on the main meeting window via AppleScript
            script = '''
            tell application "System Events"
                try
                    tell process "zoom.us"
                        -- Look for the main meeting window (usually contains "Zoom Meeting" or similar)
                        set meetingWindows to (every window whose name contains "Zoom Meeting" or name contains "Meeting" or name contains "zoom.us")
                        if (count of meetingWindows) > 0 then
                            set frontmost to true
                            click (first window of meetingWindows)
                            return "success"
                        end if
                        
                        -- If no specific meeting window, try to find any zoom window that's not participants
                        set allWindows to (every window)
                        repeat with win in allWindows
                            set winName to name of win
                            if winName does not contain "Participant" and winName does not contain "Chat" and winName does not contain "Breakout" then
                                set frontmost to true
                                click win
                                return "success"
                            end if
                        end repeat
                        
                        -- Fallback: just activate the first window
                        if (count of allWindows) > 0 then
                            set frontmost to true
                            click (first window of allWindows)
                            return "success"
                        end if
                    end tell
                end try
                return "failed"
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and "success" in result.stdout:
                self.log("Successfully focused on Zoom meeting window")
                time.sleep(1)  # Give time for window focus
                return True
            
            # Method 2: Try general Zoom app activation as fallback
            running_apps = self.workspace.runningApplications()
            for app in running_apps:
                if (app.localizedName() and 
                    'zoom' in app.localizedName().lower() and 
                    not app.isTerminated()):
                    success = app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
                    if success:
                        self.log(f"Activated Zoom application: {app.localizedName()}")
                        
                        # Try to bring the main meeting window to front
                        focus_script = '''
                        tell application "System Events"
                            tell process "zoom.us"
                                try
                                    set meetingWin to (first window whose name does not contain "Participant" and name does not contain "Chat")
                                    click meetingWin
                                end try
                            end tell
                        end tell
                        '''
                        subprocess.run(['osascript', '-e', focus_script], 
                                     capture_output=True, text=True)
                        
                        time.sleep(1)
                        return True
            
            # Method 3: Basic AppleScript activation
            script = '''
            tell application "zoom.us"
                activate
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("Activated Zoom via AppleScript")
                time.sleep(1)
                return True
                
        except Exception as e:
            self.log(f"Error activating Zoom meeting window: {e}")
        
        return False
    
    def leave_zoom_meeting(self):
        """Execute the sequence to leave Zoom meeting on macOS"""
        try:
            self.log("Attempting to leave Zoom meeting...")
            
            # Use AppleScript direct quit + Enter (fast method)
            self._method_applescript_direct_quit()
            
            self.log("✅ Leave sequence completed!")
            return True
            
        except Exception as e:
            self.log(f"Error leaving meeting: {e}")
            return False
    
    
    
    def _method_applescript_direct_quit(self):
        """Fast AppleScript quit + Enter confirmation"""
        script = '''
        tell application "zoom.us"
            quit
        end tell
        '''
        
        try:
            # Execute AppleScript quit
            subprocess.run(['osascript', '-e', script], 
                          capture_output=True, text=True, timeout=5)
            
            # Immediately press Enter to confirm
            time.sleep(0.5)  # Brief pause for dialog
            pyautogui.press('return')
            
        except Exception:
            # Fallback: just press Enter
            pyautogui.press('return')
    
    def _method_keyboard_shortcuts(self):
        """Method 3: Try various keyboard shortcuts"""
        self.log("Using keyboard shortcuts method...")
        
        # Focus on Zoom first
        if not self.activate_zoom_meeting_window():
            return False
        
        shortcuts_to_try = [
            ('cmd', 'shift', 'w'),  # Zoom's Leave Meeting shortcut
            ('cmd', 'w'),           # Close window
            ('alt', 'f4'),          # Windows-style close
            ('cmd', 'q'),           # Quit application
        ]
        
        for shortcut in shortcuts_to_try:
            try:
                self.log(f"Trying shortcut: {'+'.join(shortcut)}")
                pyautogui.hotkey(*shortcut)
                time.sleep(0.5)
                
                # Try to confirm any dialog that appears
                for _ in range(3):
                    pyautogui.press('return')
                    time.sleep(0.2)
                    pyautogui.press('enter')
                    time.sleep(0.2)
                
                # Check if it worked
                time.sleep(1)
                if not self._is_zoom_running():
                    return True
                    
            except Exception as e:
                self.log(f"Shortcut {shortcut} failed: {e}")
        
        return False
    
    def _method_force_kill(self):
        """Method 4: Force kill Zoom process as last resort"""
        self.log("Using force kill method as last resort...")
        
        try:
            # Try to kill zoom.us process
            result = subprocess.run(['pkill', '-f', 'zoom.us'], 
                                  capture_output=True, text=True, timeout=5)
            
            # Also try killall
            subprocess.run(['killall', 'zoom.us'], 
                         capture_output=True, text=True, timeout=5)
            
            return True
            
        except Exception as e:
            self.log(f"Force kill error: {e}")
            return False
    
    def _is_zoom_running(self):
        """Check if Zoom application is currently running"""
        try:
            # Method 1: Check via NSWorkspace
            running_apps = self.workspace.runningApplications()
            for app in running_apps:
                if (app.localizedName() and 
                    'zoom' in app.localizedName().lower() and 
                    not app.isTerminated()):
                    return True
            
            # Method 2: Check via AppleScript
            script = '''
            tell application "System Events"
                return (count of (every process whose name is "zoom.us")) > 0
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and "true" in result.stdout.lower():
                return True
                
            return False
            
        except Exception as e:
            self.log(f"Error checking if Zoom is running: {e}")
            return False
    
    def monitor_meeting(self):
        """Main monitoring loop"""
        self.running = True
        self.log("Starting Zoom Auto Leaver (macOS)...")
        self.log(f"Participant threshold: {self.config['participant_threshold']}")
        self.log(f"Check interval: {self.config['check_interval']} seconds")
        self.log(f"Leave shortcut: {self.config.get('leave_shortcut', 'cmd+q')}")
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
                            self.log(f"  Window {i+1}: {window['title']}")
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
        print("\n=== Zoom Auto Leaver (macOS) Configuration ===")
        print(f"Current threshold: {self.config['participant_threshold']}")
        print(f"Current check interval: {self.config['check_interval']} seconds")
        print(f"Auto-start monitoring: {self.config['auto_start']}")
        print(f"Log activity: {self.config['log_activity']}")
        print(f"Leave shortcut: {self.config.get('leave_shortcut', 'cmd+q')}")
        print(f"Confirm leave: {self.config.get('confirm_leave', True)}")
        
        while True:
            print("\nConfiguration options:")
            print("1. Set participant threshold")
            print("2. Set check interval")
            print("3. Toggle auto-start")
            print("4. Toggle logging")
            print("5. Set leave shortcut")
            print("6. Toggle confirm leave")
            print("7. Save and return to main menu")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
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
                current_shortcut = self.config.get('leave_shortcut', 'cmd+q')
                print(f"Current shortcut: {current_shortcut}")
                print("Common shortcuts:")
                print("  cmd+q - Quit application (default - most reliable)")
                print("  cmd+w - Close window (alternative)")
                print("  cmd+shift+w - Leave meeting (Zoom-specific)")
                print("  alt+q - Leave meeting (Windows-style)")
                new_shortcut = input("Enter new shortcut (e.g., 'cmd+q', 'cmd+w', 'cmd+shift+w'): ").strip()
                if new_shortcut:
                    self.config['leave_shortcut'] = new_shortcut
                    print(f"Leave shortcut set to {new_shortcut}")
            
            elif choice == '6':
                self.config['confirm_leave'] = not self.config['confirm_leave']
                print(f"Confirm leave set to {self.config['confirm_leave']}")
            
            elif choice == '7':
                self.save_config()
                print("Configuration saved!")
                break
            
            else:
                print("Invalid choice. Please try again.")

class StatusBarApp(NSObject):
    """Menu bar application controller"""
    
    def init(self):
        self = objc.super(StatusBarApp, self).init()
        if self is None:
            return None
        
        self.auto_leaver = ZoomAutoLeaverMacOS()
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Create status bar item
        self.status_bar = NSStatusBar.systemStatusBar()
        self.status_item = self.status_bar.statusItemWithLength_(NSVariableStatusItemLength)
        
        # Set icon and title
        self.status_item.setTitle_("🏃")  # Running person emoji
        self.status_item.setToolTip_("Zoom Auto Leaver")
        
        # Create menu
        self.menu = NSMenu.alloc().init()
        self.setup_menu()
        
        self.status_item.setMenu_(self.menu)
        
        return self
    
    def setup_menu(self):
        """Setup the menu bar menu"""
        # Title
        title_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Zoom Auto Leaver", None, ""
        )
        title_item.setEnabled_(False)
        self.menu.addItem_(title_item)
        
        self.menu.addItem_(NSMenuItem.separatorItem())
        
        # Monitor toggle
        self.monitor_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "▶️ Start Monitoring", "toggle_monitoring:", ""
        )
        self.monitor_item.setTarget_(self)
        self.menu.addItem_(self.monitor_item)
        
        # Status item
        self.status_text_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Status: Stopped", None, ""
        )
        self.status_text_item.setEnabled_(False)
        self.menu.addItem_(self.status_text_item)
        
        self.menu.addItem_(NSMenuItem.separatorItem())
        
        # Settings
        settings_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "⚙️ Settings", "show_settings:", ""
        )
        settings_item.setTarget_(self)
        self.menu.addItem_(settings_item)
        
        # Test functions
        test_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "🔍 Test Zoom Detection", "test_detection:", ""
        )
        test_item.setTarget_(self)
        self.menu.addItem_(test_item)
        
        test_leave_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "🚪 Test Leave Sequence", "test_leave:", ""
        )
        test_leave_item.setTarget_(self)
        self.menu.addItem_(test_leave_item)
        
        self.menu.addItem_(NSMenuItem.separatorItem())
        
        # Quit
        quit_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Quit", "quit:", "q"
        )
        quit_item.setTarget_(self)
        self.menu.addItem_(quit_item)
    
    def toggle_monitoring_(self, sender):
        """Toggle monitoring on/off"""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring in background thread"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_item.setTitle_("⏸️ Stop Monitoring")
        self.status_text_item.setTitle_(f"Status: Monitoring (threshold: {self.auto_leaver.config['participant_threshold']})")
        self.status_item.setTitle_("🔍")  # Magnifying glass when monitoring
        
        # Start monitoring in background thread
        self.monitoring_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if hasattr(self.auto_leaver, 'running'):
            self.auto_leaver.running = False
        
        self.monitor_item.setTitle_("▶️ Start Monitoring")
        self.status_text_item.setTitle_("Status: Stopped")
        self.status_item.setTitle_("🏃")  # Running person when stopped
    
    def monitor_loop(self):
        """Background monitoring loop"""
        try:
            self.auto_leaver.monitor_meeting()
        except Exception as e:
            print(f"Monitoring error: {e}")
        finally:
            # Reset UI when monitoring stops
            self.stop_monitoring()
    
    def show_settings_(self, sender):
        """Show settings dialog"""
        # For now, print to console - in future could show proper dialog
        print("\n" + "="*50)
        print("Current Settings:")
        print(f"Participant threshold: {self.auto_leaver.config['participant_threshold']}")
        print(f"Check interval: {self.auto_leaver.config['check_interval']} seconds")
        print(f"Auto-start: {self.auto_leaver.config['auto_start']}")
        print(f"Log activity: {self.auto_leaver.config['log_activity']}")
        print("="*50)
    
    def test_detection_(self, sender):
        """Test Zoom window detection"""
        print("\n🔍 Testing Zoom window detection...")
        zoom_windows = self.auto_leaver.find_zoom_windows()
        
        print(f"Found {len(zoom_windows)} Zoom window(s):")
        for i, window in enumerate(zoom_windows):
            print(f"  {i+1}. '{window['title']}' (detected via: {window['method']})")
        
        participant_count = self.auto_leaver.get_participant_count_from_windows()
        if participant_count is not None:
            print(f"\nCurrent participant count: {participant_count}")
        else:
            print("\nCould not determine participant count from window titles")
    
    def test_leave_(self, sender):
        """Test leave sequence"""
        print("\n🚪 Testing leave sequence...")
        print("Make sure you're in a Zoom meeting first!")
        success = self.auto_leaver.leave_zoom_meeting()
        print(f"Test result: {'✅ Success' if success else '❌ Failed'}")
    
    def quit_(self, sender):
        """Quit the application"""
        self.stop_monitoring()
        NSApp.terminate_(self)

def check_permissions():
    """Check if the script has necessary permissions on macOS"""
    try:
        script = '''
        tell application "System Events"
            return name of every process
        end tell
        '''
        result = subprocess.run(['osascript', '-e', script], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def main():
    # Set up the app to run as menu bar app
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)  # Don't show in dock
    
    # Check permissions
    if not check_permissions():
        print("⚠️  Warning: This app needs Accessibility permissions.")
        print("   Go to System Preferences > Security & Privacy > Privacy > Accessibility")
        print("   Add this application to the list of allowed applications.")
    
    # Create status bar app
    status_app = StatusBarApp.alloc().init()
    
    # Run the app
    print("🍎 Zoom Auto Leaver started in menu bar")
    print("Look for the 🏃 icon in your menu bar")
    print("Click it to access controls")
    
    app.run()

if __name__ == "__main__":
    main()