from __future__ import annotations

import json
from pathlib import Path


class Translator:
    def __init__(self, language: str = "bn") -> None:
        self._root = Path(__file__).parent / "locales"
        self.language = language if language in {"bn", "en"} else "bn"
        self._catalogs = {
            code: json.loads((self._root / f"{code}.json").read_text(encoding="utf-8"))
            for code in ("bn", "en")
        }

    def set_language(self, language: str) -> None:
        self.language = language if language in self._catalogs else "bn"

    def t(self, key: str, **values: object) -> str:
        text = self._catalogs[self.language].get(
            key, self._catalogs["en"].get(key, key)
        )
        return text.format(**values) if values else text
