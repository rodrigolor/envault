"""Environment variable expiry management for envault."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ExpiryError(Exception):
    """Raised for expiry-related errors."""


class ExpiryManager:
    """Manages expiry dates for environment variable keys."""

    _FILENAME = "expiry.json"

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / self._FILENAME
        self._data: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def set_expiry(self, key: str, expires_at: datetime) -> None:
        """Set an expiry datetime (UTC) for a key."""
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        self._data[key] = expires_at.isoformat()
        self._save()

    def get_expiry(self, key: str) -> Optional[datetime]:
        """Return the expiry datetime for a key, or None if not set."""
        raw = self._data.get(key)
        if raw is None:
            return None
        return datetime.fromisoformat(raw)

    def remove_expiry(self, key: str) -> None:
        """Remove the expiry for a key. Raises ExpiryError if not set."""
        if key not in self._data:
            raise ExpiryError(f"No expiry set for key: {key!r}")
        del self._data[key]
        self._save()

    def is_expired(self, key: str) -> bool:
        """Return True if the key has an expiry that is in the past."""
        expiry = self.get_expiry(key)
        if expiry is None:
            return False
        now = datetime.now(tz=timezone.utc)
        return now >= expiry

    def list_expiring(self) -> dict[str, datetime]:
        """Return a mapping of all keys that have an expiry set."""
        return {k: datetime.fromisoformat(v) for k, v in self._data.items()}

    def list_expired(self) -> list[str]:
        """Return keys whose expiry has already passed."""
        return [k for k in self._data if self.is_expired(k)]
