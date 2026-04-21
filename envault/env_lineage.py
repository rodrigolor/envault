"""Track the lineage (origin/derivation chain) of environment variable keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class LineageError(Exception):
    """Raised when a lineage operation fails."""


class LineageManager:
    """Persist and query key derivation / origin metadata."""

    _FILENAME = "lineage.json"

    def __init__(self, base_dir: str) -> None:
        self._path = Path(base_dir) / self._FILENAME
        self._data: Dict[str, Dict] = self._load()

    def _load(self) -> Dict[str, Dict]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))

    def record(self, key: str, origin: str, derived_from: Optional[str] = None) -> None:
        """Record that *key* originated from *origin* (e.g. 'manual', 'import', 'copy').

        Optionally specify the parent key it was derived from.
        """
        if not key:
            raise LineageError("Key must not be empty.")
        self._data[key] = {
            "origin": origin,
            "derived_from": derived_from,
        }
        self._save()

    def get(self, key: str) -> Optional[Dict]:
        """Return lineage info for *key*, or None if not recorded."""
        return self._data.get(key)

    def derived_from(self, parent_key: str) -> List[str]:
        """Return all keys that were derived from *parent_key*."""
        return [
            k for k, v in self._data.items() if v.get("derived_from") == parent_key
        ]

    def remove(self, key: str) -> None:
        """Remove lineage record for *key*."""
        if key not in self._data:
            raise LineageError(f"No lineage record found for '{key}'.")
        del self._data[key]
        self._save()

    def list_all(self) -> Dict[str, Dict]:
        """Return all recorded lineage data."""
        return dict(self._data)
