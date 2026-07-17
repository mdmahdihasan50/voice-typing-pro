from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir, user_data_dir


@dataclass(slots=True)
class AppSettings:
    ui_language: str = "bn"
    dictation_language: str = "bn-BD"
    typing_mode: str = "internal"
    theme: str = "system"
    speech_engine: str = "google"
    listening_mode: str = "continuous"
    offline_model: str = "small"
    microphone_index: int | None = None
    font_family: str = "Noto Sans Bengali"
    font_size: int = 17
    auto_save: bool = True
    voice_commands: bool = True
    automatic_punctuation: bool = True
    bengali_digits: bool = False
    floating_bar_visible: bool = True
    floating_x: int | None = None
    floating_y: int | None = None
    always_on_top: bool = False
    start_with_windows: bool = False
    launch_minimized: bool = False
    hotkey_toggle: str = "<ctrl>+<shift>+<space>"
    hotkey_bengali: str = "<alt>+<shift>+b"
    hotkey_english: str = "<alt>+<shift>+e"
    window_geometry: str = ""
    last_file: str = ""
    recent_files: list[str] = field(default_factory=list)


class SettingsStore:
    def __init__(self, path: Path | None = None) -> None:
        base = Path(user_config_dir("VoiceTypingPro", "Mahdi Hasan"))
        self.path = path or base / "settings.json"
        self.data_dir = (
            path.parent / "data"
            if path is not None
            else Path(user_data_dir("VoiceTypingPro", "Mahdi Hasan"))
        )

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            allowed = {item.name for item in fields(AppSettings)}
            values = {key: value for key, value in raw.items() if key in allowed}
            return AppSettings(**values)
        except (OSError, ValueError, TypeError):
            return AppSettings()

    def save(self, settings: AppSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(asdict(settings), ensure_ascii=False, indent=2)
        fd, temp_name = tempfile.mkstemp(
            prefix="settings-", suffix=".tmp", dir=self.path.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
            os.replace(temp_name, self.path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    @property
    def autosave_path(self) -> Path:
        return self.data_dir / "autosave.txt"

    @property
    def history_path(self) -> Path:
        return self.data_dir / "history.json"


def update_settings(settings: AppSettings, values: dict[str, Any]) -> AppSettings:
    allowed = {item.name for item in fields(AppSettings)}
    for key, value in values.items():
        if key in allowed:
            setattr(settings, key, value)
    return settings
