"""Read-only key management for envault."""

from __future__ import annotations

import json
from pathlib import Path


class ReadOnlyError(Exception):
    """Raised when a read-only constraint is violated."""


class ReadOnlyManager:
    """Manages a set of keys that are protected from modification or deletion."""

    _FILENAME = "readonly.json"

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / self._FILENAME
        self._keys: set[str] = self._load()

    def _load(self) -> set[str]:
        if not self._path.exists():
            return set()
        with self._path.open() as fh:
            data = json.load(fh)
        return set(data.get("readonly", []))

    def _save(self) -> None:
        with self._path.open("w") as fh:
            json.dump({"readonly": sorted(self._keys)}, fh, indent=2)

    def protect(self, key: str) -> None:
        """Mark *key* as read-only."""
        self._keys.add(key)
        self._save()

    def unprotect(self, key: str) -> None:
        """Remove read-only protection from *key*."""
        if key not in self._keys:
            raise ReadOnlyError(f"Key '{key}' is not marked as read-only.")
        self._keys.discard(key)
        self._save()

    def is_readonly(self, key: str) -> bool:
        """Return True if *key* is protected."""
        return key in self._keys

    def list_readonly(self) -> list[str]:
        """Return a sorted list of all read-only keys."""
        return sorted(self._keys)

    def guard(self, key: str, action: str = "modify") -> None:
        """Raise :class:`ReadOnlyError` if *key* is protected.

        Parameters
        ----------
        key:
            The environment variable name to check.
        action:
            A short description of the attempted operation used in the error
            message (e.g. ``"modify"`` or ``"delete"``).  Defaults to
            ``"modify"``.
        """
        if self.is_readonly(key):
            raise ReadOnlyError(
                f"Cannot {action} '{key}': key is marked as read-only."
            )
