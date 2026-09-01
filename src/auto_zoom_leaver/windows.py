from __future__ import annotations

import time
from collections.abc import Callable, Iterable, Iterator
from typing import Any

from .participants import parse_participant_count


class WindowsZoomAdapter:
    def __init__(
        self,
        desktop_factory: Callable[[], Any] | None = None,
        process_iter: Callable[..., Iterable[Any]] | None = None,
        hotkey: Callable[..., None] | None = None,
        sleep: Callable[[float], None] = time.sleep,
        logger: Callable[[str], None] = lambda _message: None,
        prompt_delay: float = 0.5,
    ) -> None:
        self._desktop_factory = desktop_factory
        self._process_iter = process_iter
        self._hotkey = hotkey
        self._sleep = sleep
        self._logger = logger
        self._prompt_delay = prompt_delay

    def _dependencies(
        self,
    ) -> tuple[
        Callable[[], Any],
        Callable[..., Iterable[Any]],
        Callable[..., None],
    ]:
        if (
            self._desktop_factory is not None
            and self._process_iter is not None
            and self._hotkey is not None
        ):
            return self._desktop_factory, self._process_iter, self._hotkey

        try:
            import psutil
            import pyautogui
            from pywinauto import Desktop
        except ImportError as error:
            raise RuntimeError(
                "Windows dependencies are missing. Install requirements.txt first."
            ) from error

        self._desktop_factory = lambda: Desktop(backend="uia")
        self._process_iter = psutil.process_iter
        self._hotkey = pyautogui.hotkey
        return self._desktop_factory, self._process_iter, self._hotkey

    def check_availability(self) -> bool:
        """Load the UI Automation backend without inspecting or changing Zoom."""
        try:
            desktop_factory, _, _ = self._dependencies()
            if desktop_factory() is None:
                raise RuntimeError("UI Automation desktop could not be created")
        except Exception as error:
            raise RuntimeError("UI Automation backend is unavailable") from error
        return True

    def _zoom_processes(self) -> list[Any]:
        _, process_iter, _ = self._dependencies()
        processes = []
        try:
            candidates = process_iter(["name"])
            for process in candidates:
                try:
                    name = str(process.info.get("name") or "").strip()
                    if name.casefold() == "zoom.exe":
                        processes.append(process)
                except (AttributeError, KeyError, OSError):
                    continue
        except OSError as error:
            self._logger(f"Windows could not list processes: {error}")
        return processes

    @staticmethod
    def _controls(root: Any) -> Iterator[Any]:
        yield root
        for child in root.children():
            yield from WindowsZoomAdapter._controls(child)

    @staticmethod
    def _control_info(control: Any) -> tuple[str, str]:
        info = control.element_info
        control_type = str(getattr(info, "control_type", "") or "").strip()
        name = str(getattr(info, "name", "") or "").strip()
        return control_type, name

    def _windows_and_controls(self) -> list[tuple[Any, list[Any]]]:
        desktop_factory, _, _ = self._dependencies()
        desktop = desktop_factory()
        records = []
        for process in self._zoom_processes():
            try:
                windows = list(desktop.windows(process=process.pid))
                for window in windows:
                    records.append((window, list(self._controls(window))))
            except Exception as error:
                raise RuntimeError(
                    "Zoom's UI Automation tree is inaccessible."
                ) from error
        return records

    def get_participant_count(self) -> int | None:
        try:
            records = self._windows_and_controls()
            counts = {
                count
                for _, controls in records
                for control in controls
                for count in [parse_participant_count(self._control_info(control)[1])]
                if count is not None
            }
        except Exception as error:
            self._logger(f"Participant controls are inaccessible: {error}")
            return None

        if len(counts) != 1:
            if len(counts) > 1:
                self._logger("Participant controls are ambiguous. Retrying.")
            else:
                self._logger("No participant control was found. Retrying.")
            return None
        return counts.pop()

    @staticmethod
    def _is_safe_leave_button(control: Any) -> bool:
        control_type, name = WindowsZoomAdapter._control_info(control)
        if (
            control_type.casefold() != "button"
            or name.replace("&", "").casefold() != "leave meeting"
        ):
            return False
        enabled = getattr(control, "is_enabled", True)
        if callable(enabled):
            enabled = enabled()
        return bool(enabled) and callable(getattr(control, "invoke", None))

    def leave_meeting(self) -> bool:
        try:
            records = self._windows_and_controls()
            if not records:
                self._logger("Zoom window was not found. Leave cancelled.")
                return False

            window = records[0][0]
            set_focus = getattr(window, "set_focus", None)
            if callable(set_focus):
                set_focus()
            _, _, hotkey = self._dependencies()
            hotkey("alt", "q")
            self._sleep(self._prompt_delay)

            prompt_records = self._windows_and_controls()
            buttons = [
                control
                for _, controls in prompt_records
                for control in controls
                if self._is_safe_leave_button(control)
            ]
            if len(buttons) != 1:
                self._logger(
                    "Leave Meeting control is missing or ambiguous. No control was invoked."
                )
                return False
            buttons[0].invoke()
            return True
        except Exception as error:
            self._logger(f"Leave failed without invoking a control: {error}")
            return False
