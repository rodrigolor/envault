"""Diff utilities for comparing vault states."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


class DiffError(Exception):
    """Raised when a diff operation fails."""


@dataclass
class DiffResult:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    modified: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.modified)

    def summary(self) -> str:
        lines = []
        for key, value in self.added.items():
            lines.append(f"+ {key}={value}")
        for key, value in self.removed.items():
            lines.append(f"- {key}={value}")
        for key, (old, new) in self.modified.items():
            lines.append(f"~ {key}: {old!r} -> {new!r}")
        return "\n".join(lines) if lines else "No changes."


class DiffManager:
    """Compares two vault states and reports differences."""

    def __init__(self, vault) -> None:
        self._vault = vault

    def compare(self, other: Dict[str, str]) -> DiffResult:
        """Compare the current vault state against a given dict snapshot."""
        try:
            current = self._vault.get_all()
        except Exception as exc:
            raise DiffError(f"Failed to read vault: {exc}") from exc

        result = DiffResult()

        for key, value in other.items():
            if key not in current:
                result.removed[key] = value
            elif current[key] != value:
                result.modified[key] = (value, current[key])

        for key, value in current.items():
            if key not in other:
                result.added[key] = value

        return result

    def compare_snapshots(
        self, snapshot_a: Dict[str, str], snapshot_b: Dict[str, str]
    ) -> DiffResult:
        """Compare two arbitrary snapshots without touching the vault."""
        result = DiffResult()

        for key, value in snapshot_a.items():
            if key not in snapshot_b:
                result.removed[key] = value
            elif snapshot_b[key] != value:
                result.modified[key] = (value, snapshot_b[key])

        for key, value in snapshot_b.items():
            if key not in snapshot_a:
                result.added[key] = value

        return result
