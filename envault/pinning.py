"""Variable pinning — lock specific keys to prevent accidental overwrites."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


class PinError(Exception):
    """Raised when a pinning operation fails."""


class PinManager:
    """Manages a set of pinned (write-protected) vault keys."""

    _FILENAME = "pins.json"

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / self._FILENAME
        self._pins: List[str] = self._load()

    def _load(self) -> List[str]:
        if not self._path.exists():
            return []
        try:
            data = json.loads(self._path.read_text())
            return data.get("pins", [])
        except (json.JSONDecodeError, KeyError):
            return []

    def _save(self) -> None:
        self._path.write_text(json.dumps({"pins": self._pins}, indent=2))

    def pin(self, key: str) -> None:
        """Pin *key* so it cannot be overwritten without unpinning first."""
        if key in self._pins:
            raise PinError(f"Key '{key}' is already pinned.")
        self._pins.append(key)
        self._save()

    def unpin(self, key: str) -> None:
        """Remove the pin from *key*."""
        if key not in self._pins:
            raise PinError(f"Key '{key}' is not pinned.")
        self._pins.remove(key)
        self._save()

    def is_pinned(self, key: str) -> bool:
        """Return True if *key* is currently pinned."""
        return key in self._pins

    def list_pins(self) -> List[str]:
        """Return a sorted list of all pinned keys."""
        return sorted(self._pins)

    def assert_writable(self, key: str) -> None:
        """Raise *PinError* if *key* is pinned."""
        if self.is_pinned(key):
            raise PinError(
                f"Key '{key}' is pinned and cannot be modified. "
                "Run 'envault pin unpin {key}' to remove the pin."
            )
