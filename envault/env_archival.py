"""Archival management for environment variables — mark keys as archived and retrieve them."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional


class ArchivalError(Exception):
    """Raised when an archival operation fails."""


class ArchivalManager:
    """Manages archival state for vault keys."""

    _FILENAME = "archival.json"

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / self._FILENAME
        self._data: Dict[str, Dict] = self._load()

    def _load(self) -> Dict[str, Dict]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def archive(self, key: str, reason: Optional[str] = None) -> None:
        """Mark a key as archived."""
        if key in self._data:
            raise ArchivalError(f"Key '{key}' is already archived.")
        self._data[key] = {
            "archived_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason or "",
        }
        self._save()

    def unarchive(self, key: str) -> None:
        """Remove a key from the archived set."""
        if key not in self._data:
            raise ArchivalError(f"Key '{key}' is not archived.")
        del self._data[key]
        self._save()

    def is_archived(self, key: str) -> bool:
        """Return True if the key is currently archived."""
        return key in self._data

    def get_info(self, key: str) -> Optional[Dict]:
        """Return archival metadata for a key, or None if not archived."""
        return self._data.get(key)

    def list_archived(self) -> List[str]:
        """Return a sorted list of all archived keys."""
        return sorted(self._data.keys())
