from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable

from src.auto_zoom_leaver.config import ConfigStore
from src.auto_zoom_leaver.monitor import MeetingMonitor
from src.auto_zoom_leaver.windows import WindowsZoomAdapter


class ZoomAutoLeaver:
    def __init__(
        self,
        config_file: str | Path | None = None,
        adapter: WindowsZoomAdapter | None = None,
    ) -> None:
        self.store = ConfigStore(path=Path(config_file) if config_file else None)
        self.config = self.store.load()
        self.adapter = adapter or WindowsZoomAdapter(logger=self.log)
        self.monitor: MeetingMonitor | None = None

    def save_config(self) -> None:
        self.store.save(self.config)

    def log(self, message: str) -> None:
        if not self.config.get("log_activity", True):
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        print(formatted)
        try:
            self.store.log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.store.log_path.open("a", encoding="utf-8") as log_file:
                log_file.write(formatted + "\n")
        except OSError as error:
            print(f"Could not write activity log: {error}")

    def get_participant_count(self) -> int | None:
        return self.adapter.get_participant_count()

    def leave_zoom_meeting(self) -> bool:
        return self.adapter.leave_meeting()

    def monitor_meeting(self) -> bool:
        self.monitor = MeetingMonitor(
            self.adapter,
            threshold=int(self.config["participant_threshold"]),
            interval=int(self.config["check_interval"]),
            logger=self.log,
        )
        self.log("Starting Zoom Auto Leaver.")
        self.log(f"Participant threshold: {self.config['participant_threshold']}")
        self.log(f"Check interval: {self.config['check_interval']} seconds")
        return self.monitor.run()

    def stop_monitoring(self) -> None:
        if self.monitor is not None:
            self.monitor.stop()

    def configure(self, input_fn: Callable[[str], str] = input) -> None:
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
            choice = input_fn("\nEnter your choice (1-5): ").strip()

            if choice == "1":
                try:
                    threshold = int(
                        input_fn(
                            f"Enter participant threshold (current: {self.config['participant_threshold']}): "
                        )
                    )
                    if threshold >= 0:
                        self.config["participant_threshold"] = threshold
                        print(f"Threshold set to {threshold}")
                    else:
                        print("Threshold must not be negative")
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "2":
                try:
                    interval = int(
                        input_fn(
                            f"Enter check interval in seconds (current: {self.config['check_interval']}): "
                        )
                    )
                    if interval > 0:
                        self.config["check_interval"] = interval
                        print(f"Check interval set to {interval} seconds")
                    else:
                        print("Interval must be greater than 0")
                except ValueError:
                    print("Please enter a valid number")
            elif choice == "3":
                self.config["auto_start"] = not self.config["auto_start"]
                print(f"Auto-start set to {self.config['auto_start']}")
            elif choice == "4":
                self.config["log_activity"] = not self.config["log_activity"]
                print(f"Logging set to {self.config['log_activity']}")
            elif choice == "5":
                self.save_config()
                print("Configuration saved!")
                return
            else:
                print("Invalid choice. Please try again.")


def main() -> int:
    auto_leaver = ZoomAutoLeaver()
    if auto_leaver.config["auto_start"]:
        auto_leaver.monitor_meeting()
        return 0

    while True:
        print("\n=== Zoom Auto Leaver ===")
        print("1. Start monitoring")
        print("2. Configure settings")
        print("3. Test Zoom participant detection")
        print("4. Exit")
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            auto_leaver.monitor_meeting()
        elif choice == "2":
            auto_leaver.configure()
        elif choice == "3":
            count = auto_leaver.get_participant_count()
            if count is None:
                print("Participant count is unavailable. The monitor will retry.")
            else:
                print(f"Current participant count: {count}")
        elif choice == "4":
            print("Goodbye!")
            return 0
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    raise SystemExit(main())
