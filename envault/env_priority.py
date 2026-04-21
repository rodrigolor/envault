"""Priority management for environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class PriorityError(Exception):
    """Raised when a priority operation fails."""


PRIORITY_LEVELS = ("low", "normal", "high", "critical")


class PriorityManager:
    """Manage load/override priority levels for environment variable keys."""

    def __init__(self, vault_dir: str) -> None:
        self._path = Path(vault_dir) / "priorities.json"
        self._data: Dict[str, str] = self._load()

    def _load(self) -> Dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def set_priority(self, key: str, level: str) -> None:
        """Assign a priority level to a key."""
        if level not in PRIORITY_LEVELS:
            raise PriorityError(
                f"Invalid priority '{level}'. Choose from: {', '.join(PRIORITY_LEVELS)}"
            )
        self._data[key] = level
        self._save()

    def remove_priority(self, key: str) -> None:
        """Remove a priority assignment from a key."""
        if key not in self._data:
            raise PriorityError(f"Key '{key}' has no priority set.")
        del self._data[key]
        self._save()

    def get_priority(self, key: str) -> Optional[str]:
        """Return the priority level for a key, or None if not set."""
        return self._data.get(key)

    def list_by_level(self, level: str) -> List[str]:
        """Return all keys assigned to a given priority level."""
        if level not in PRIORITY_LEVELS:
            raise PriorityError(
                f"Invalid priority '{level}'. Choose from: {', '.join(PRIORITY_LEVELS)}"
            )
        return [k for k, v in self._data.items() if v == level]

    def list_all(self) -> Dict[str, str]:
        """Return a mapping of all keys to their priority levels."""
        return dict(self._data)
