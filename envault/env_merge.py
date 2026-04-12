"""Merge multiple vault sources or .env files into the active vault."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional


class MergeError(Exception):
    """Raised when a merge operation fails."""


class MergeResult:
    def __init__(self, added: List[str], updated: List[str], skipped: List[str]):
        self.added = added
        self.updated = updated
        self.skipped = skipped

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.updated)

    def summary(self) -> str:
        return (
            f"Added: {len(self.added)}, "
            f"Updated: {len(self.updated)}, "
            f"Skipped: {len(self.skipped)}"
        )


class EnvMerger:
    def __init__(self, vault) -> None:
        self._vault = vault

    def merge(self, source: Dict[str, str], overwrite: bool = False) -> MergeResult:
        """Merge a dict of key/value pairs into the vault."""
        added: List[str] = []
        updated: List[str] = []
        skipped: List[str] = []

        for key, value in source.items():
            existing = self._vault.get(key)
            if existing is None:
                self._vault.set(key, value)
                added.append(key)
            elif overwrite:
                self._vault.set(key, value)
                updated.append(key)
            else:
                skipped.append(key)

        return MergeResult(added=added, updated=updated, skipped=skipped)

    def merge_file(self, path: Path, overwrite: bool = False) -> MergeResult:
        """Merge a .env file into the vault."""
        if not path.exists():
            raise MergeError(f"File not found: {path}")

        pairs: Dict[str, str] = {}
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise MergeError(f"Invalid line in env file: {line!r}")
            key, _, value = line.partition("=")
            pairs[key.strip()] = value.strip().strip('"\'')

        return self.merge(pairs, overwrite=overwrite)
