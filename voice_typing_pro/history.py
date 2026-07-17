from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class HistoryStore:
    def __init__(self, path: Path, limit: int = 100) -> None:
        self.path = path
        self.limit = limit

    def load(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (OSError, ValueError):
            return []

    def add(self, text: str, language: str) -> None:
        if not text.strip():
            return
        items = self.load()
        items.insert(
            0,
            {
                "text": text.strip(),
                "language": language,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(items[: self.limit], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def clear(self) -> None:
        try:
            self.path.unlink(missing_ok=True)
        except OSError:
            pass
