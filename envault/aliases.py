"""Alias management for envault — map short names to vault keys."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


class AliasError(Exception):
    """Raised when an alias operation fails."""


class AliasManager:
    """Manages key aliases stored in a JSON file."""

    def __init__(self, base_dir: str | Path) -> None:
        self._path = Path(base_dir) / "aliases.json"
        self._aliases: Dict[str, str] = self._load()

    def _load(self) -> Dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._aliases, indent=2))

    def add(self, alias: str, key: str) -> None:
        """Register *alias* as a short-hand for vault *key*."""
        if not alias or not key:
            raise AliasError("Alias and key must be non-empty strings.")
        if alias in self._aliases:
            raise AliasError(f"Alias '{alias}' already exists.")
        self._aliases[alias] = key
        self._save()

    def remove(self, alias: str) -> None:
        """Delete an existing alias."""
        if alias not in self._aliases:
            raise AliasError(f"Alias '{alias}' not found.")
        del self._aliases[alias]
        self._save()

    def resolve(self, alias: str) -> Optional[str]:
        """Return the vault key for *alias*, or ``None`` if unknown."""
        return self._aliases.get(alias)

    def list_aliases(self) -> Dict[str, str]:
        """Return a copy of all alias → key mappings."""
        return dict(self._aliases)

    def rename(self, old_alias: str, new_alias: str) -> None:
        """Rename an existing alias without changing its target key."""
        if old_alias not in self._aliases:
            raise AliasError(f"Alias '{old_alias}' not found.")
        if new_alias in self._aliases:
            raise AliasError(f"Alias '{new_alias}' already exists.")
        self._aliases[new_alias] = self._aliases.pop(old_alias)
        self._save()
