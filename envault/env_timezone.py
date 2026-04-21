"""Timezone metadata manager for environment variable timestamps."""

from __future__ import annotations

import json
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimezoneError(Exception):
    """Raised when a timezone operation fails."""


class TimezoneManager:
    """Store and retrieve timezone associations for vault keys."""

    _FILENAME = "env_timezones.json"

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / self._FILENAME
        self._data: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def set_timezone(self, key: str, tz: str) -> None:
        """Associate *tz* (IANA timezone string) with *key*."""
        try:
            ZoneInfo(tz)
        except (ZoneInfoNotFoundError, KeyError):
            raise TimezoneError(f"Unknown timezone: {tz!r}")
        self._data[key] = tz
        self._save()

    def get_timezone(self, key: str) -> str | None:
        """Return the timezone string for *key*, or None if unset."""
        return self._data.get(key)

    def remove_timezone(self, key: str) -> None:
        """Remove the timezone association for *key*."""
        if key not in self._data:
            raise TimezoneError(f"No timezone set for key: {key!r}")
        del self._data[key]
        self._save()

    def list_all(self) -> dict[str, str]:
        """Return a copy of all key → timezone mappings."""
        return dict(self._data)

    def keys_in_timezone(self, tz: str) -> list[str]:
        """Return all keys that are associated with *tz*."""
        return [k for k, v in self._data.items() if v == tz]
