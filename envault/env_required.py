"""Manage required environment variable declarations for a vault."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List


class RequiredError(Exception):
    """Raised when a required-keys operation fails."""


class RequiredManager:
    """Track which keys are required and validate their presence."""

    _FILENAME = "required.json"

    def __init__(self, base_dir: str | Path) -> None:
        self._path = Path(base_dir) / self._FILENAME
        self._required: List[str] = self._load()

    def _load(self) -> List[str]:
        if not self._path.exists():
            return []
        with self._path.open() as fh:
            data = json.load(fh)
        return data.get("required", [])

    def _save(self) -> None:
        with self._path.open("w") as fh:
            json.dump({"required": self._required}, fh, indent=2)

    def mark_required(self, key: str) -> None:
        """Mark *key* as required."""
        if key in self._required:
            raise RequiredError(f"Key '{key}' is already marked as required.")
        self._required.append(key)
        self._save()

    def unmark_required(self, key: str) -> None:
        """Remove the required mark from *key*."""
        if key not in self._required:
            raise RequiredError(f"Key '{key}' is not marked as required.")
        self._required.remove(key)
        self._save()

    def is_required(self, key: str) -> bool:
        """Return True if *key* is marked required."""
        return key in self._required

    def list_required(self) -> List[str]:
        """Return a sorted list of all required keys."""
        return sorted(self._required)

    def validate(self, vault_keys: List[str]) -> List[str]:
        """Return required keys missing from *vault_keys*."""
        present = set(vault_keys)
        return [k for k in self._required if k not in present]
