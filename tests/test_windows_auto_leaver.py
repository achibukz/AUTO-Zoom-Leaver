import json

import pytest

from auto_zoom_leaver.config import ConfigStore, default_storage_dir
from auto_zoom_leaver.monitor import MeetingMonitor
from auto_zoom_leaver.participants import parse_participant_count
from auto_zoom_leaver.windows import WindowsZoomAdapter


class FakeInfo:
    def __init__(self, control_type="Window", name="", class_name="", automation_id=""):
        self.control_type = control_type
        self.name = name
        self.class_name = class_name
        self.automation_id = automation_id


class FakeControl:
    def __init__(self, control_type="Window", name="", children=(), enabled=True):
        self.element_info = FakeInfo(control_type=control_type, name=name)
        self._children = list(children)
        self.is_enabled = enabled
        self.invoked = False
        self.focused = False

    def children(self):
        return self._children

    def set_focus(self):
        self.focused = True

    def invoke(self):
        self.invoked = True


class FakeProcess:
    pid = 123
    info = {"name": "Zoom.exe"}


class FakeDesktop:
    def __init__(self, windows):
        self._windows = windows

    def windows(self, process):
        return self._windows


def make_adapter(windows, process_iter=None, hotkey=None, sleep=None, logger=None):
    return WindowsZoomAdapter(
        desktop_factory=lambda: FakeDesktop(windows),
        process_iter=process_iter or (lambda *_args: [FakeProcess()]),
        hotkey=hotkey or (lambda *_keys: None),
        sleep=sleep or (lambda _seconds: None),
        logger=logger or (lambda _message: None),
    )


def test_default_storage_dir_uses_localappdata(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "Local"))

    assert default_storage_dir() == tmp_path / "Local" / "AutoZoomLeaver"


def test_config_migrates_valid_values_from_repository_config(tmp_path):
    legacy_path = tmp_path / "config.json"
    local_path = tmp_path / "Local" / "AutoZoomLeaver" / "config.json"
    legacy_path.write_text(
        json.dumps(
            {
                "participant_threshold": 2,
                "check_interval": 4,
                "auto_start": True,
                "log_activity": False,
                "leave_shortcut": "cmd+q",
            }
        ),
        encoding="utf-8",
    )

    config = ConfigStore(path=local_path, legacy_path=legacy_path).load()

    assert config == {
        "participant_threshold": 2,
        "check_interval": 4,
        "auto_start": True,
        "log_activity": False,
    }
    assert json.loads(local_path.read_text(encoding="utf-8")) == config


def test_invalid_configuration_values_fall_back_individually(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "participant_threshold": -1,
                "check_interval": "fast",
                "auto_start": "yes",
                "log_activity": False,
            }
        ),
        encoding="utf-8",
    )

    assert ConfigStore(path=config_path).load() == {
        "participant_threshold": 5,
        "check_interval": 10,
        "auto_start": False,
        "log_activity": False,
    }


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Participants (2)", 2),
        ("participants: 7", 7),
        ("2 Participants", 2),
        ("(0) Participants", 0),
        ("attendees (4)", 4),
        ("Meeting ID: 123 456 7890", None),
        ("Room 42", None),
        ("", None),
    ],
)
def test_parse_participant_count_uses_supported_labels_only(label, expected):
    assert parse_participant_count(label) == expected


class SequenceAdapter:
    def __init__(self, counts, leave_result=True):
        self.counts = iter(counts)
        self.leave_result = leave_result
        self.leave_calls = 0

    def get_participant_count(self):
        return next(self.counts)

    def leave_meeting(self):
        self.leave_calls += 1
        return self.leave_result


@pytest.mark.parametrize("count", [4, 5])
def test_monitor_leaves_at_or_below_threshold(count):
    adapter = SequenceAdapter([count])

    left = MeetingMonitor(adapter, threshold=5, interval=10).run(max_polls=1)

    assert left is True
    assert adapter.leave_calls == 1


def test_monitor_waits_above_threshold_and_retries_missing_counts():
    adapter = SequenceAdapter([None, 6])
    sleeps = []

    left = MeetingMonitor(
        adapter, threshold=5, interval=10, sleep=sleeps.append
    ).run(max_polls=2)

    assert left is False
    assert adapter.leave_calls == 0
    assert sleeps == [10]


def test_windows_adapter_reads_a_single_fixture_count():
    root = FakeControl(
        children=[
            FakeControl("Window", "Participants (2)"),
            FakeControl("Text", "Meeting ID: 123 456 7890"),
        ]
    )

    assert make_adapter([root]).get_participant_count() == 2


def test_windows_adapter_retries_when_zoom_is_missing():
    adapter = make_adapter([], process_iter=lambda *_args: [])

    assert adapter.get_participant_count() is None


def test_windows_adapter_retries_when_windows_expose_ambiguous_counts():
    root = FakeControl(
        children=[
            FakeControl("Window", "Participants (2)"),
            FakeControl("Window", "Participants (3)"),
        ]
    )

    assert make_adapter([root]).get_participant_count() is None


def test_windows_adapter_retries_when_tree_is_inaccessible():
    class BrokenControl:
        @property
        def element_info(self):
            raise RuntimeError("inaccessible")

    assert make_adapter([BrokenControl()]).get_participant_count() is None


def test_leave_invokes_only_one_exact_safe_button():
    safe_button = FakeControl("Button", "&Leave Meeting")
    end_button = FakeControl("Button", "End Meeting for All")
    hotkeys = []
    root = FakeControl(children=[end_button, safe_button])
    adapter = make_adapter([root], hotkey=lambda *keys: hotkeys.append(keys))

    assert adapter.leave_meeting() is True
    assert hotkeys == [("alt", "q")]
    assert safe_button.invoked is True
    assert end_button.invoked is False


@pytest.mark.parametrize("button_names", [[], ["Leave Meeting", "Leave Meeting"]])
def test_leave_fails_closed_without_clicking_ambiguous_safe_controls(button_names):
    buttons = [FakeControl("Button", name) for name in button_names]
    root = FakeControl(children=buttons)
    logs = []
    adapter = make_adapter([root], logger=logs.append)

    assert adapter.leave_meeting() is False
    assert all(button.invoked is False for button in buttons)
    assert any("Leave Meeting" in message for message in logs)
