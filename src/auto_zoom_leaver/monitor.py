from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol


class MonitorAdapter(Protocol):
    def get_participant_count(self) -> int | None: ...

    def leave_meeting(self) -> bool: ...


class MeetingMonitor:
    def __init__(
        self,
        adapter: MonitorAdapter,
        threshold: int,
        interval: int,
        sleep: Callable[[float], None] = time.sleep,
        logger: Callable[[str], None] = lambda _message: None,
    ) -> None:
        self.adapter = adapter
        self.threshold = threshold
        self.interval = interval
        self.sleep = sleep
        self.logger = logger
        self.running = False

    def stop(self) -> None:
        self.running = False

    def run(self, max_polls: int | None = None) -> bool:
        self.running = True
        polls = 0
        try:
            while self.running and (max_polls is None or polls < max_polls):
                polls += 1
                try:
                    count = self.adapter.get_participant_count()
                except Exception as error:
                    self.logger(f"Participant detection failed: {error}")
                    count = None

                if count is None:
                    self.logger("Participant count unavailable. Retrying.")
                elif count <= self.threshold:
                    self.logger(
                        f"Participant count ({count}) reached threshold ({self.threshold})."
                    )
                    try:
                        left = self.adapter.leave_meeting()
                    except Exception as error:
                        self.logger(f"Leave attempt failed: {error}")
                        left = False
                    if left:
                        self.logger("Meeting left successfully.")
                        return True
                    self.logger("Leave attempt failed. Retrying.")
                else:
                    self.logger(f"Participant count is {count}.")

                if max_polls is not None and polls >= max_polls:
                    break
                self.sleep(self.interval)
        finally:
            self.running = False
        return False
