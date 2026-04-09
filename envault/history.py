"""History tracking for environment variable changes."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class HistoryError(Exception):
    """Raised when a history operation fails."""


class HistoryManager:
    """Records and retrieves the change history of vault keys."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.history_file = self.base_dir / "history.json"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, list[dict[str, Any]]]:
        if not self.history_file.exists():
            return {}
        with self.history_file.open() as fh:
            return json.load(fh)

    def _save(self, data: dict[str, list[dict[str, Any]]]) -> None:
        with self.history_file.open("w") as fh:
            json.dump(data, fh, indent=2)

    def record(self, key: str, action: str, actor: str = "cli") -> None:
        """Record a change event for *key*.

        Args:
            key: The vault key that was modified.
            action: One of 'set', 'delete', 'rotate'.
            actor: Free-form string identifying who made the change.
        """
        data = self._load()
        entry = {
            "action": action,
            "actor": actor,
            "timestamp": time.time(),
        }
        data.setdefault(key, []).append(entry)
        self._save(data)

    def get_history(self, key: str) -> list[dict[str, Any]]:
        """Return all recorded events for *key*, oldest first."""
        return self._load().get(key, [])

    def list_keys(self) -> list[str]:
        """Return all keys that have at least one history entry."""
        return list(self._load().keys())

    def clear(self, key: str | None = None) -> None:
        """Clear history for *key*, or all history if *key* is None."""
        if key is None:
            self._save({})
        else:
            data = self._load()
            data.pop(key, None)
            self._save(data)
