"""Snapshot management for envault — capture and restore vault state."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


class SnapshotError(Exception):
    """Raised when a snapshot operation fails."""


class SnapshotManager:
    """Create, list, and restore named snapshots of vault variables."""

    SNAPSHOT_FILE = "snapshots.json"

    def __init__(self, vault, base_dir: Path) -> None:
        self._vault = vault
        self._path = Path(base_dir) / self.SNAPSHOT_FILE
        self._data: Dict[str, dict] = self._load()

    def _load(self) -> Dict[str, dict]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def create(self, name: str) -> None:
        """Capture current vault state under *name*."""
        if name in self._data:
            raise SnapshotError(f"Snapshot '{name}' already exists.")
        variables = self._vault.get_all()
        self._data[name] = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "variables": variables,
        }
        self._save()

    def restore(self, name: str) -> int:
        """Restore vault to the state captured in *name*. Returns number of keys restored."""
        if name not in self._data:
            raise SnapshotError(f"Snapshot '{name}' not found.")
        variables: Dict[str, str] = self._data[name]["variables"]
        for key, value in variables.items():
            self._vault.set(key, value)
        return len(variables)

    def delete(self, name: str) -> None:
        """Remove a snapshot by name."""
        if name not in self._data:
            raise SnapshotError(f"Snapshot '{name}' not found.")
        del self._data[name]
        self._save()

    def list_snapshots(self) -> List[dict]:
        """Return metadata for all snapshots, sorted by creation time."""
        result = [
            {"name": n, "created_at": v["created_at"], "count": len(v["variables"])}
            for n, v in self._data.items()
        ]
        return sorted(result, key=lambda x: x["created_at"])

    def get(self, name: str) -> Optional[Dict[str, str]]:
        """Return the variables stored in a snapshot, or None if not found."""
        entry = self._data.get(name)
        return entry["variables"] if entry else None
