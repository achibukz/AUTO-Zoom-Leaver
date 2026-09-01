import json
from pathlib import Path

import pytest

from tools.windows_zoom_diagnostic import (
    DiagnosticError,
    WindowsZoomAccessibility,
    collect_report,
    normalize_label,
    run_diagnostic,
    sanitize_capture,
    write_report_atomic,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "windows_zoom_report.json"


def test_returned_windows_report_fixture_has_only_sanitized_selector_data():
    report = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert report["schema_version"] == 1
    assert [capture["capture_type"] for capture in report["captures"]] == [
        "participant_meeting",
        "participant_leave_prompt",
        "host_leave_prompt",
    ]

    labels = {
        control["normalized_label"]
        for capture in report["captures"]
        for process in capture["processes"]
        for control in process["controls"]
        if control["normalized_label"] != "<redacted>"
    }
    assert labels == {
        "Participants (1)",
        "Participants (2)",
        "Leave Meeting",
        "End Meeting for All",
    }

    serialized = json.dumps(report)
    assert "Alicia" not in serialized
    assert "@" not in serialized
    assert "123 456 7890" not in serialized

    for process in [
        process
        for capture in report["captures"]
        for process in capture["processes"]
    ]:
        assert process["process_name"] == "Zoom.exe"
        for control in process["controls"]:
            assert "name" not in control
            assert set(control) == {
                "control_type",
                "class_name",
                "automation_id",
                "hierarchy",
                "normalized_label",
            }


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Participants (4)", "Participants (4)"),
        ("participants: 7", "Participants (7)"),
        ("2 Participants", "Participants (2)"),
        ("(0) Participants", "Participants (0)"),
        ("Leave Meeting", "Leave Meeting"),
        ("&Leave Meeting", "Leave Meeting"),
        ("End Meeting for All", "End Meeting for All"),
        ("Alicia Santos", "<redacted>"),
        ("alicia@example.com", "<redacted>"),
        ("Meeting ID: 123 456 7890", "<redacted>"),
        ("Weekly planning", "<redacted>"),
    ],
)
def test_normalize_label_redacts_private_and_unknown_text(label, expected):
    assert normalize_label(label) == expected


def test_sanitize_capture_keeps_metadata_without_raw_ui_text():
    capture = {
        "capture_type": "participant_leave_prompt",
        "processes": [
            {
                "process_name": "Zoom.exe",
                "controls": [
                    {
                        "control_type": "Button",
                        "class_name": "ButtonClass",
                        "automation_id": "leaveButton",
                        "hierarchy": ["Window", "Pane", "Button"],
                        "name": "Leave Meeting",
                    },
                    {
                        "control_type": "Text",
                        "class_name": "TextClass",
                        "automation_id": "meeting-123 456 7890",
                        "hierarchy": ["Window", "Text"],
                        "name": "Alicia Santos alicia@example.com",
                    },
                ],
            }
        ],
    }

    sanitized = sanitize_capture(capture)
    serialized = json.dumps(sanitized)

    assert sanitized["processes"][0]["controls"][0]["normalized_label"] == "Leave Meeting"
    assert sanitized["processes"][0]["controls"][1]["normalized_label"] == "<redacted>"
    assert "Alicia Santos" not in serialized
    assert "alicia@example.com" not in serialized
    assert "123 456 7890" not in serialized
    assert "<redacted>" in serialized


def test_write_report_atomic_writes_complete_json(tmp_path: Path):
    report_path = tmp_path / "AutoZoomLeaver" / "report.json"

    write_report_atomic({"schema_version": 1, "captures": []}, report_path)

    assert json.loads(report_path.read_text(encoding="utf-8")) == {
        "schema_version": 1,
        "captures": [],
    }
    assert list(report_path.parent.glob("*.tmp")) == []


class _FakeProcess:
    pid = 123
    info = {"name": "Zoom.exe"}


class _FakeElementInfo:
    def __init__(self, control_type, name):
        self.control_type = control_type
        self.class_name = "ZoomControl"
        self.automation_id = "stable-id"
        self.name = name


class _ReadOnlyControl:
    def __init__(self, control_type, name, children=()):
        self.element_info = _FakeElementInfo(control_type, name)
        self._children = list(children)
        self.click_input_called = False
        self.invoke_called = False

    def children(self):
        return self._children

    def click_input(self):
        self.click_input_called = True
        raise AssertionError("diagnostic must not click controls")

    def invoke(self):
        self.invoke_called = True
        raise AssertionError("diagnostic must not invoke controls")


class _FakeDesktop:
    def __init__(self, windows):
        self._windows = windows

    def windows(self, process):
        return self._windows


def test_capture_reads_tree_without_input_or_invocation_methods():
    leave_button = _ReadOnlyControl("Button", "Leave Meeting")
    root = _ReadOnlyControl("Window", "Weekly planning", [leave_button])
    diagnostic = WindowsZoomAccessibility(
        desktop_factory=lambda: _FakeDesktop([root]),
        process_iter=lambda *_args: [_FakeProcess()],
    )

    capture = diagnostic.capture("participant_leave_prompt")

    assert capture["processes"][0]["controls"][1]["name"] == "Leave Meeting"
    assert leave_button.click_input_called is False
    assert leave_button.invoke_called is False


def test_missing_zoom_process_is_actionable():
    diagnostic = WindowsZoomAccessibility(
        desktop_factory=lambda: _FakeDesktop([]),
        process_iter=lambda *_args: [],
    )

    with pytest.raises(DiagnosticError, match="Zoom was not found"):
        diagnostic.capture("participant_meeting")


def test_inaccessible_tree_does_not_produce_a_capture():
    class BrokenControl:
        @property
        def element_info(self):
            raise RuntimeError("inaccessible")

    diagnostic = WindowsZoomAccessibility(
        desktop_factory=lambda: _FakeDesktop([BrokenControl()]),
        process_iter=lambda *_args: [_FakeProcess()],
    )

    with pytest.raises(DiagnosticError, match="UI Automation tree"):
        diagnostic.capture("host_leave_prompt")


def test_collect_report_only_returns_sanitized_three_capture_report():
    class FakeDiagnostic:
        def capture(self, capture_type):
            return {
                "capture_type": capture_type,
                "processes": [
                    {
                        "process_name": "Zoom.exe",
                        "controls": [
                            {
                                "control_type": "Button",
                                "class_name": "Button",
                                "automation_id": "id",
                                "hierarchy": ["Window", "Button"],
                                "name": "End Meeting for All"
                                if capture_type == "host_leave_prompt"
                                else "Leave Meeting",
                            }
                        ],
                    }
                ],
            }

    report = collect_report(
        FakeDiagnostic(),
        input_fn=lambda _prompt: "",
        output_fn=lambda _message: None,
    )

    assert [capture["capture_type"] for capture in report["captures"]] == [
        "participant_meeting",
        "participant_leave_prompt",
        "host_leave_prompt",
    ]
    labels = [
        capture["processes"][0]["controls"][0]["normalized_label"]
        for capture in report["captures"]
    ]
    assert labels == ["Leave Meeting", "Leave Meeting", "End Meeting for All"]


def test_failed_capture_does_not_write_a_partial_report(tmp_path: Path):
    class FailingDiagnostic:
        def __init__(self):
            self.capture_count = 0

        def capture(self, capture_type):
            self.capture_count += 1
            if self.capture_count == 2:
                raise DiagnosticError("Zoom's UI Automation tree is inaccessible")
            return {"capture_type": capture_type, "processes": []}

    report_path = tmp_path / "report.json"

    with pytest.raises(DiagnosticError):
        run_diagnostic(
            FailingDiagnostic(),
            report_path,
            input_fn=lambda _prompt: "",
            output_fn=lambda _message: None,
        )

    assert report_path.exists() is False
