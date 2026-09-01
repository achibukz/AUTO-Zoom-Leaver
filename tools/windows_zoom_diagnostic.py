#!/usr/bin/env python3
"""Read-only Zoom UI Automation diagnostic for Windows.

The diagnostic never activates, clicks, invokes, or sends input to a control.
The operator performs the three capture actions manually while this program
only reads the Microsoft UI Automation tree.
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping


REPORT_FILENAME = "report.json"
REDACTED = "<redacted>"
CAPTURE_KINDS = (
    "participant_meeting",
    "participant_leave_prompt",
    "host_leave_prompt",
)

_PARTICIPANT_PATTERNS = (
    re.compile(r"^participants?\s*\(\s*(\d{1,5})\s*\)$", re.IGNORECASE),
    re.compile(r"^participants?\s*:\s*(\d{1,5})$", re.IGNORECASE),
    re.compile(r"^participants?\s+(\d{1,5})$", re.IGNORECASE),
    re.compile(r"^(\d{1,5})\s+participants?$", re.IGNORECASE),
    re.compile(r"^\(\s*(\d{1,5})\s*\)\s*participants?$", re.IGNORECASE),
    re.compile(r"^attendees?\s*\(\s*(\d{1,5})\s*\)$", re.IGNORECASE),
    re.compile(r"^people\s*\(\s*(\d{1,5})\s*\)$", re.IGNORECASE),
)
_MEETING_ID_PATTERN = re.compile(r"\b\d{3}[ -]?\d{3}[ -]?\d{4}\b")


class DiagnosticError(RuntimeError):
    """An actionable failure while reading Zoom's accessibility tree."""


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _participant_count(value: str) -> int | None:
    for pattern in _PARTICIPANT_PATTERNS:
        match = pattern.fullmatch(value)
        if match is not None:
            count = int(match.group(1))
            if 0 <= count <= 10000:
                return count
    return None


def normalize_label(value: str) -> str:
    """Keep the small set of labels needed to choose safe selectors."""

    label = _clean_text(value).replace("&", "")
    folded = label.casefold()
    if folded == "leave meeting":
        return "Leave Meeting"
    if folded == "end meeting for all":
        return "End Meeting for All"

    count = _participant_count(label)
    if count is not None:
        return f"Participants ({count})"

    return REDACTED


def _sanitize_metadata(value: Any) -> str:
    """Remove a meeting ID if Zoom includes one in technical metadata."""

    metadata = _clean_text(value)
    return _MEETING_ID_PATTERN.sub(REDACTED, metadata)


def sanitize_capture(capture: Mapping[str, Any]) -> dict[str, Any]:
    """Create the only report representation that may be written to disk."""

    processes: list[dict[str, Any]] = []
    for process in capture.get("processes", []):
        controls: list[dict[str, Any]] = []
        for control in process.get("controls", []):
            controls.append(
                {
                    "control_type": _clean_text(control.get("control_type")),
                    "class_name": _sanitize_metadata(control.get("class_name")),
                    "automation_id": _sanitize_metadata(control.get("automation_id")),
                    "hierarchy": [
                        _clean_text(item) for item in control.get("hierarchy", [])
                    ],
                    "normalized_label": normalize_label(control.get("name", "")),
                }
            )
        processes.append(
            {
                "process_name": _clean_text(process.get("process_name")),
                "controls": controls,
            }
        )

    return {
        "capture_type": _clean_text(capture.get("capture_type")),
        "processes": processes,
    }


class WindowsZoomAccessibility:
    """Read Zoom controls through pywinauto's Microsoft UIA backend."""

    def __init__(
        self,
        desktop_factory: Callable[[], Any] | None = None,
        process_iter: Callable[..., Iterable[Any]] | None = None,
    ) -> None:
        self._desktop_factory = desktop_factory
        self._process_iter = process_iter

    def _dependencies(self) -> tuple[Callable[[], Any], Callable[..., Iterable[Any]]]:
        if self._desktop_factory is not None and self._process_iter is not None:
            return self._desktop_factory, self._process_iter

        try:
            import psutil
            from pywinauto import Desktop
        except ImportError as error:
            raise DiagnosticError(
                "The Windows diagnostic dependencies are missing. "
                "Run the packaged executable or install its requirements."
            ) from error

        self._desktop_factory = lambda: Desktop(backend="uia")
        self._process_iter = psutil.process_iter
        return self._desktop_factory, self._process_iter

    def _zoom_processes(self) -> list[Any]:
        _, process_iter = self._dependencies()
        processes: list[Any] = []
        try:
            candidates = process_iter(["name"])
            for process in candidates:
                try:
                    name = _clean_text(process.info.get("name"))
                    if "zoom" in name.casefold():
                        processes.append(process)
                except (AttributeError, KeyError, OSError):
                    continue
        except OSError as error:
            raise DiagnosticError(
                "Windows could not list processes. Restart the diagnostic and try again."
            ) from error

        if not processes:
            raise DiagnosticError(
                "Zoom was not found. Start Zoom, open the requested state, and retry."
            )
        return processes

    @staticmethod
    def _control_info(control: Any) -> tuple[str, str, str, str]:
        try:
            info = control.element_info
            control_type = _clean_text(info.control_type) or "Unknown"
            class_name = _clean_text(info.class_name)
            automation_id = _clean_text(info.automation_id)
            name = _clean_text(info.name)
            return control_type, class_name, automation_id, name
        except Exception as error:
            raise DiagnosticError(
                "Zoom's UI Automation tree could not be read. "
                "Keep the requested Zoom window open and retry."
            ) from error

    def _walk_control(
        self,
        control: Any,
        parent_hierarchy: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        control_type, class_name, automation_id, name = self._control_info(control)
        hierarchy = parent_hierarchy + (control_type,)
        record = {
            "control_type": control_type,
            "class_name": class_name,
            "automation_id": automation_id,
            "hierarchy": list(hierarchy),
            "name": name,
        }
        try:
            children = list(control.children())
        except Exception as error:
            raise DiagnosticError(
                "Zoom's UI Automation tree is inaccessible. "
                "Keep the requested Zoom window open and retry."
            ) from error

        controls = [record]
        for child in children:
            controls.extend(self._walk_control(child, hierarchy))
        return controls

    def capture(self, capture_type: str) -> dict[str, Any]:
        if capture_type not in CAPTURE_KINDS:
            raise ValueError(f"Unsupported capture type: {capture_type}")

        desktop_factory, _ = self._dependencies()
        processes = self._zoom_processes()
        try:
            desktop = desktop_factory()
            process_records: list[dict[str, Any]] = []
            for process in processes:
                process_name = _clean_text(process.info.get("name"))
                windows = list(desktop.windows(process=process.pid))
                controls: list[dict[str, Any]] = []
                for window in windows:
                    controls.extend(self._walk_control(window, ()))
                if controls:
                    process_records.append(
                        {"process_name": process_name, "controls": controls}
                    )
        except DiagnosticError:
            raise
        except Exception as error:
            raise DiagnosticError(
                "Zoom's UI Automation tree is inaccessible. "
                "Keep the requested Zoom window open and retry."
            ) from error

        if not process_records:
            raise DiagnosticError(
                "Zoom is running, but no accessible UI Automation controls were found. "
                "Open the requested Zoom window and retry."
            )

        return {"capture_type": capture_type, "processes": process_records}


def write_report_atomic(report: Mapping[str, Any], output_path: Path) -> None:
    """Write a complete report without exposing an intermediate file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f"{output_path.stem}-", suffix=".tmp", dir=output_path.parent
    )
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8") as output_file:
            json.dump(report, output_file, indent=2)
            output_file.write("\n")
            output_file.flush()
            os.fsync(output_file.fileno())
        os.replace(temporary_name, output_path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def collect_report(
    diagnostic: WindowsZoomAccessibility,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> dict[str, Any]:
    """Guide the operator through all captures and return a sanitized report."""

    instructions = {
        "participant_meeting": (
            "Join a disposable meeting as a participant. Leave the meeting window "
            "and participant panel visible, then press Enter."
        ),
        "participant_leave_prompt": (
            "As a participant, manually press Alt+Q in Zoom and leave the prompt "
            "visible. Do not click a button, then press Enter here."
        ),
        "host_leave_prompt": (
            "Join a disposable meeting as host. Manually press Alt+Q in Zoom and "
            "leave the prompt visible. Do not click a button, then press Enter here."
        ),
    }
    captures: list[dict[str, Any]] = []
    for capture_type in CAPTURE_KINDS:
        output_fn(f"\n{instructions[capture_type]}")
        input_fn("Press Enter to read the current Zoom UI Automation tree: ")
        captures.append(sanitize_capture(diagnostic.capture(capture_type)))

    return {"schema_version": 1, "captures": captures}


def default_report_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "AutoZoomLeaver" / REPORT_FILENAME
    return Path.cwd() / REPORT_FILENAME


def run_diagnostic(
    diagnostic: WindowsZoomAccessibility,
    output_path: Path,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> None:
    """Collect every capture before replacing the previous report."""

    report = collect_report(diagnostic, input_fn=input_fn, output_fn=output_fn)
    write_report_atomic(report, output_path)


def main() -> int:
    output_path = default_report_path()
    print("Auto Zoom Leaver Windows diagnostic")
    print("This program only reads Zoom's UI Automation tree.")
    print(f"A sanitized report will be written to: {output_path}")

    try:
        run_diagnostic(WindowsZoomAccessibility(), output_path)
    except (DiagnosticError, OSError) as error:
        print(f"Capture failed: {error}", file=sys.stderr)
        print("No report was written.", file=sys.stderr)
        return 1

    print(f"Capture complete. Return this file to Aki: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
