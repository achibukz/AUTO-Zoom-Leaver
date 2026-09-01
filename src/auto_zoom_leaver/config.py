from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Mapping


CONFIG_FILENAME = "config.json"
LOG_FILENAME = "activity.log"
DEFAULT_CONFIG = {
    "participant_threshold": 5,
    "check_interval": 10,
    "auto_start": False,
    "log_activity": True,
}


def default_storage_dir(
    environ: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    environment = os.environ if environ is None else environ
    local_app_data = environment.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "AutoZoomLeaver"
    return (home or Path.home()) / "AutoZoomLeaver"


def default_config_path() -> Path:
    return default_storage_dir() / CONFIG_FILENAME


def activity_log_path() -> Path:
    return default_storage_dir() / LOG_FILENAME


def validate_config(values: object) -> dict[str, object]:
    config = dict(DEFAULT_CONFIG)
    if not isinstance(values, Mapping):
        return config

    threshold = values.get("participant_threshold")
    if (
        isinstance(threshold, int)
        and not isinstance(threshold, bool)
        and threshold >= 0
    ):
        config["participant_threshold"] = threshold

    interval = values.get("check_interval")
    if (
        isinstance(interval, int)
        and not isinstance(interval, bool)
        and interval > 0
    ):
        config["check_interval"] = interval

    auto_start = values.get("auto_start")
    if isinstance(auto_start, bool):
        config["auto_start"] = auto_start

    log_activity = values.get("log_activity")
    if isinstance(log_activity, bool):
        config["log_activity"] = log_activity

    return config


class ConfigStore:
    def __init__(
        self,
        path: Path | None = None,
        legacy_path: Path | None = None,
    ) -> None:
        self.path = path or default_config_path()
        self.legacy_path = legacy_path or (Path.cwd() / CONFIG_FILENAME)
        self.log_path = self.path.with_name(LOG_FILENAME)

    def load(self) -> dict[str, object]:
        source_path = self.path if self.path.exists() else self.legacy_path
        values: object = {}
        if source_path.exists():
            try:
                values = json.loads(source_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                values = {}

        config = validate_config(values)
        if source_path != self.path or not self.path.exists():
            self.save(config)
        return config

    def save(self, values: Mapping[str, object]) -> None:
        config = validate_config(values)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(config, indent=4) + "\n", encoding="utf-8")
