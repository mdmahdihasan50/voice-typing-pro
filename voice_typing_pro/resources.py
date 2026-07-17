from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QFontDatabase


def register_bundled_fonts() -> list[str]:
    font_dir = Path(__file__).parent / "assets" / "fonts"
    loaded: list[str] = []
    for font_path in font_dir.glob("*.ttf"):
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id >= 0:
            loaded.extend(QFontDatabase.applicationFontFamilies(font_id))
    return loaded
