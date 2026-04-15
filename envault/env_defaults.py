"""Manage default values for environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


class DefaultsError(Exception):
    """Raised when a defaults operation fails."""


class DefaultsManager:
    """Stores and applies default values for vault keys."""

    _FILENAME = "defaults.json"

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / self._FILENAME
        self._defaults: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._defaults, indent=2))

    def set_default(self, key: str, value: Any) -> None:
        """Register a default value for *key*."""
        self._defaults[key] = value
        self._save()

    def remove_default(self, key: str) -> None:
        """Remove the default for *key*."""
        if key not in self._defaults:
            raise DefaultsError(f"No default registered for '{key}'")
        del self._defaults[key]
        self._save()

    def get_default(self, key: str) -> Optional[Any]:
        """Return the default value for *key*, or None."""
        return self._defaults.get(key)

    def list_defaults(self) -> Dict[str, Any]:
        """Return a copy of all registered defaults."""
        return dict(self._defaults)

    def apply(self, vault: Any) -> Dict[str, str]:
        """Set defaults in *vault* for any key not already present.

        Returns a mapping of keys that were actually written.
        """
        applied: Dict[str, str] = {}
        existing = vault.get_all()
        for key, value in self._defaults.items():
            if key not in existing:
                vault.set(key, str(value))
                applied[key] = str(value)
        return applied
