"""Remote configuration management for envault sync backends."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class RemoteError(Exception):
    """Raised when a remote operation fails."""


class RemoteManager:
    """Manages named remote backend configurations."""

    SUPPORTED_TYPES = {"file", "s3", "gcs"}

    def __init__(self, base_dir: str | Path) -> None:
        self._path = Path(base_dir) / "remotes.json"
        self._remotes: Dict[str, dict] = self._load()

    def _load(self) -> Dict[str, dict]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._remotes, indent=2))

    def add(self, name: str, remote_type: str, url: str, **options: str) -> None:
        """Register a new remote."""
        if name in self._remotes:
            raise RemoteError(f"Remote '{name}' already exists.")
        if remote_type not in self.SUPPORTED_TYPES:
            raise RemoteError(
                f"Unsupported remote type '{remote_type}'. "
                f"Choose from: {sorted(self.SUPPORTED_TYPES)}"
            )
        self._remotes[name] = {"type": remote_type, "url": url, **options}
        self._save()

    def remove(self, name: str) -> None:
        """Remove a registered remote."""
        if name not in self._remotes:
            raise RemoteError(f"Remote '{name}' not found.")
        del self._remotes[name]
        self._save()

    def get(self, name: str) -> dict:
        """Return the configuration for a remote."""
        if name not in self._remotes:
            raise RemoteError(f"Remote '{name}' not found.")
        return dict(self._remotes[name])

    def list_remotes(self) -> List[str]:
        """Return all registered remote names."""
        return list(self._remotes.keys())

    def update(self, name: str, **fields: str) -> None:
        """Update fields of an existing remote."""
        if name not in self._remotes:
            raise RemoteError(f"Remote '{name}' not found.")
        self._remotes[name].update(fields)
        self._save()
