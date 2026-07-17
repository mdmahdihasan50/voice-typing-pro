from __future__ import annotations

import os
import sys
from pathlib import Path


def configure_windows_startup(enabled: bool) -> None:
    if sys.platform != "win32":
        return
    import winreg

    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    executable = Path(sys.executable)
    if getattr(sys, "frozen", False):
        command = f'"{executable}" --minimized'
    else:
        main_file = Path(__file__).resolve().parents[1] / "main.py"
        command = f'"{executable}" "{main_file}" --minimized'
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE
    ) as key:
        if enabled:
            winreg.SetValueEx(key, "VoiceTypingPro", 0, winreg.REG_SZ, command)
        else:
            try:
                winreg.DeleteValue(key, "VoiceTypingPro")
            except FileNotFoundError:
                pass
