import sys
from pathlib import Path

import pytest

from auto_zoom_leaver.config import (
    ConfigStore,
    DEFAULT_CONFIG,
    activity_log_path,
    default_storage_dir,
)
from auto_zoom_leaver.windows import WindowsZoomAdapter
from zoom_auto_leaver import main, run_self_test


class AvailableAutomation:
    def __call__(self):
        return object()


def test_source_storage_falls_back_to_home_without_localappdata(tmp_path):
    assert default_storage_dir(environ={}, home=tmp_path) == (
        tmp_path / "AutoZoomLeaver"
    )


def test_default_config_and_log_paths_use_localappdata(monkeypatch, tmp_path):
    local_app_data = tmp_path / "LocalAppData"
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))

    store = ConfigStore()

    assert store.path == local_app_data / "AutoZoomLeaver" / "config.json"
    assert activity_log_path() == local_app_data / "AutoZoomLeaver" / "activity.log"


def test_frozen_store_does_not_read_current_directory_config(
    monkeypatch, tmp_path
):
    local_app_data = tmp_path / "LocalAppData"
    working_directory = tmp_path / "working"
    working_directory.mkdir()
    (working_directory / "config.json").write_text(
        '{"participant_threshold": 99}', encoding="utf-8"
    )
    monkeypatch.chdir(working_directory)
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    monkeypatch.setattr(sys, "frozen", True, raising=False)

    config = ConfigStore().load()

    assert config == DEFAULT_CONFIG
    assert local_app_data.joinpath("AutoZoomLeaver", "config.json").exists()


def test_ui_automation_availability_can_be_checked_without_zoom_windows():
    adapter = WindowsZoomAdapter(
        desktop_factory=AvailableAutomation(),
        process_iter=lambda *_args: [],
        hotkey=lambda *_keys: None,
    )

    assert adapter.check_availability() is True


def test_ui_automation_availability_rejects_a_missing_desktop():
    adapter = WindowsZoomAdapter(
        desktop_factory=lambda: None,
        process_iter=lambda *_args: [],
        hotkey=lambda *_keys: None,
    )

    with pytest.raises(RuntimeError, match="unavailable"):
        adapter.check_availability()


def test_self_test_checks_config_and_ui_automation(tmp_path):
    config_path = tmp_path / "AutoZoomLeaver" / "config.json"
    config_path.parent.mkdir()
    config_path.write_text("{}", encoding="utf-8")

    adapter = WindowsZoomAdapter(
        desktop_factory=AvailableAutomation(),
        process_iter=lambda *_args: [],
        hotkey=lambda *_keys: None,
    )

    assert run_self_test(
        store_factory=lambda: ConfigStore(path=config_path),
        adapter_factory=lambda: adapter,
    ) is True


def test_self_test_reports_ui_automation_failure(tmp_path, capsys):
    config_path = tmp_path / "AutoZoomLeaver" / "config.json"
    config_path.parent.mkdir()
    config_path.write_text("{}", encoding="utf-8")

    def unavailable():
        raise RuntimeError("UI Automation is unavailable")

    adapter = WindowsZoomAdapter(
        desktop_factory=unavailable,
        process_iter=lambda *_args: [],
        hotkey=lambda *_keys: None,
    )

    assert run_self_test(
        store_factory=lambda: ConfigStore(path=config_path),
        adapter_factory=lambda: adapter,
    ) is False
    assert "Self-test failed" in capsys.readouterr().err


def test_self_test_rejects_missing_configuration_keys(capsys):
    class EmptyStore:
        def load(self):
            return {}

    assert run_self_test(
        store_factory=EmptyStore,
        adapter_factory=AvailableAutomation,
    ) is False
    assert "required settings" in capsys.readouterr().err


def test_self_test_rejects_a_false_ui_automation_result(capsys):
    class ValidStore:
        def load(self):
            return dict(DEFAULT_CONFIG)

    class UnavailableAdapter:
        def check_availability(self):
            return False

    assert run_self_test(
        store_factory=ValidStore,
        adapter_factory=UnavailableAdapter,
    ) is False
    assert "unavailable" in capsys.readouterr().err


def test_self_test_flag_returns_a_failure_code_when_checks_fail(monkeypatch):
    monkeypatch.setattr("zoom_auto_leaver.run_self_test", lambda: False)

    assert main(["--self-test"]) == 1


def test_main_rejects_unknown_arguments(capsys):
    assert main(["--unknown"]) == 2
    assert "Unknown argument" in capsys.readouterr().err


def test_packaging_spec_supports_both_build_modes():
    spec = Path("tools/windows_auto_leaver.spec").read_text(encoding="utf-8")

    assert 'AUTO_ZOOM_LEAVER_BUILD_MODE' in spec
    assert '"onedir"' in spec
    assert "COLLECT(" in spec
    assert 'name="AutoZoomLeaver"' in spec


def test_windows_build_script_runs_and_validates_each_stage():
    script = Path("tools/build_windows.ps1").read_text(encoding="utf-8")
    requirements = Path("requirements_windows.txt").read_text(encoding="utf-8")

    assert "python -m venv" in script
    assert "pip install" in script
    assert "requirements_windows.txt" in script
    assert "-r requirements.txt" in requirements
    assert "pyinstaller==6.11.1" in requirements
    assert "pytest==8.3.4" in requirements
    assert "pytest" in script
    assert "AUTO_ZOOM_LEAVER_BUILD_MODE" in script
    assert "onedir" in script
    assert "onefile" in script
    assert "$LASTEXITCODE" in script
    assert "Stage failed" in script
    assert "AutoZoomLeaver.exe" in script


def test_generated_windows_artifacts_are_ignored():
    ignored = {
        line.strip()
        for line in Path(".gitignore").read_text(encoding="utf-8").splitlines()
    }

    assert ".venv-build/" in ignored
    assert "build/" in ignored
    assert "dist/" in ignored
    assert "*.exe" in ignored
