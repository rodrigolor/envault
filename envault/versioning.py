"""Key versioning support for envault — track multiple versions of a secret."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class VersionError(Exception):
    """Raised when a versioning operation fails."""


class VersionManager:
    """Manages multiple historical versions of vault keys."""

    MAX_VERSIONS = 10

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / "versions.json"
        self._data: dict[str, list[dict[str, Any]]] = self._load()

    def _load(self) -> dict[str, list[dict[str, Any]]]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def record(self, key: str, value: str) -> None:
        """Record a new version of *key* with the given *value*."""
        versions = self._data.setdefault(key, [])
        versions.append({"value": value, "timestamp": time.time()})
        # Trim to the most recent MAX_VERSIONS entries
        if len(versions) > self.MAX_VERSIONS:
            self._data[key] = versions[-self.MAX_VERSIONS :]
        self._save()

    def list_versions(self, key: str) -> list[dict[str, Any]]:
        """Return all recorded versions for *key*, oldest first."""
        return list(self._data.get(key, []))

    def get_version(self, key: str, index: int) -> str:
        """Return the value at *index* (0 = oldest) for *key*.

        Raises VersionError if the key or index is invalid.
        """
        versions = self._data.get(key)
        if not versions:
            raise VersionError(f"No version history for key '{key}'")
        try:
            return versions[index]["value"]
        except IndexError:
            raise VersionError(
                f"Version index {index} out of range for key '{key}' "
                f"(has {len(versions)} version(s))"
            )

    def rollback(self, key: str, vault: Any) -> str:
        """Restore the previous version of *key* in *vault*.

        Returns the restored value.  Raises VersionError when there is
        no previous version to roll back to.
        """
        versions = self._data.get(key, [])
        if len(versions) < 2:
            raise VersionError(
                f"Not enough history to roll back key '{key}'"
            )
        previous = versions[-2]["value"]
        vault.set(key, previous)
        return previous

    def clear(self, key: str) -> None:
        """Delete all version history for *key*."""
        self._data.pop(key, None)
        self._save()
