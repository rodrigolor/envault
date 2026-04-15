"""Track and warn about deprecated environment variable keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class DeprecationError(Exception):
    """Raised when a deprecation operation fails."""


class DeprecationManager:
    """Manage deprecated environment variable keys with optional replacement hints."""

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / "deprecations.json"
        self._data: dict[str, dict] = self._load()

    def _load(self) -> dict[str, dict]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def mark_deprecated(self, key: str, reason: str = "", replacement: Optional[str] = None) -> None:
        """Mark a key as deprecated with an optional reason and replacement."""
        if not key:
            raise DeprecationError("Key must not be empty.")
        self._data[key] = {"reason": reason, "replacement": replacement}
        self._save()

    def unmark_deprecated(self, key: str) -> None:
        """Remove the deprecated status of a key."""
        if key not in self._data:
            raise DeprecationError(f"Key '{key}' is not marked as deprecated.")
        del self._data[key]
        self._save()

    def is_deprecated(self, key: str) -> bool:
        """Return True if the key is deprecated."""
        return key in self._data

    def get_info(self, key: str) -> Optional[dict]:
        """Return deprecation info for a key, or None if not deprecated."""
        return self._data.get(key)

    def list_deprecated(self) -> dict[str, dict]:
        """Return all deprecated keys and their info."""
        return dict(self._data)

    def warn_if_deprecated(self, key: str) -> Optional[str]:
        """Return a warning message if the key is deprecated, else None."""
        info = self._data.get(key)
        if info is None:
            return None
        msg = f"Warning: '{key}' is deprecated."
        if info.get("reason"):
            msg += f" Reason: {info['reason']}."
        if info.get("replacement"):
            msg += f" Use '{info['replacement']}' instead."
        return msg
