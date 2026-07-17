from __future__ import annotations

from pathlib import Path

import PyInstaller.__main__
from PySide6.QtWidgets import QApplication

from voice_typing_pro.widgets import create_app_icon


if __name__ == "__main__":
    application = QApplication.instance() or QApplication([])
    icon_dir = Path("build_assets")
    icon_dir.mkdir(exist_ok=True)
    icon_path = icon_dir / "app_icon.png"
    if not create_app_icon(256).pixmap(256, 256).save(str(icon_path)):
        raise RuntimeError("Could not generate the application icon")
    PyInstaller.__main__.run(
        [
            "main.py",
            "--name=BanglaVoiceTypingPro",
            "--onefile",
            "--windowed",
            "--clean",
            "--noconfirm",
            f"--icon={icon_path}",
            "--collect-all=speech_recognition",
            "--collect-all=faster_whisper",
            "--add-data=voice_typing_pro/locales;voice_typing_pro/locales",
            "--add-data=voice_typing_pro/assets;voice_typing_pro/assets",
            "--exclude-module=customtkinter",
        ]
    )
