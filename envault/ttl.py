"""TTL (time-to-live) management for environment variables."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional


class TTLError(Exception):
    """Raised when a TTL operation fails."""


class TTLManager:
    """Manages expiry times for individual vault keys."""

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / ".ttl.json"
        self._data: dict[str, float] = self._load()

    def _load(self) -> dict[str, float]:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text())
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def set_ttl(self, key: str, seconds: float) -> None:
        """Assign a TTL to *key*, expiring *seconds* from now."""
        if seconds <= 0:
            raise TTLError("TTL must be a positive number of seconds.")
        self._data[key] = time.time() + seconds
        self._save()

    def is_expired(self, key: str) -> bool:
        """Return True if *key* has a TTL that has already passed."""
        expiry = self._data.get(key)
        if expiry is None:
            return False
        return time.time() > expiry

    def time_remaining(self, key: str) -> Optional[float]:
        """Return seconds remaining for *key*, or None if no TTL is set."""
        expiry = self._data.get(key)
        if expiry is None:
            return None
        remaining = expiry - time.time()
        return max(remaining, 0.0)

    def clear_ttl(self, key: str) -> None:
        """Remove the TTL for *key* (key will never expire)."""
        self._data.pop(key, None)
        self._save()

    def purge_expired(self) -> list[str]:
        """Remove all expired TTL entries and return the list of expired keys."""
        now = time.time()
        expired = [k for k, exp in self._data.items() if now > exp]
        for k in expired:
            del self._data[k]
        if expired:
            self._save()
        return expired

    def all_ttls(self) -> dict[str, float]:
        """Return a mapping of key -> seconds remaining (only live entries)."""
        now = time.time()
        return {
            k: max(exp - now, 0.0)
            for k, exp in self._data.items()
            if now <= exp
        }
