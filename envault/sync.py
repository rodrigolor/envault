"""Sync module for envault — handles pushing/pulling vault data to/from remote backends."""

import json
import os
from pathlib import Path
from typing import Optional


class SyncBackend:
    """Base class for sync backends."""

    def push(self, data: bytes, remote_path: str) -> None:
        raise NotImplementedError

    def pull(self, remote_path: str) -> Optional[bytes]:
        raise NotImplementedError

    def exists(self, remote_path: str) -> bool:
        raise NotImplementedError


class FileSyncBackend(SyncBackend):
    """Sync backend that uses a shared local/network filesystem path."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def push(self, data: bytes, remote_path: str) -> None:
        target = self.base_dir / remote_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

    def pull(self, remote_path: str) -> Optional[bytes]:
        target = self.base_dir / remote_path
        if not target.exists():
            return None
        return target.read_bytes()

    def exists(self, remote_path: str) -> bool:
        return (self.base_dir / remote_path).exists()


class SyncManager:
    """Manages syncing an encrypted vault file to/from a remote backend."""

    def __init__(self, backend: SyncBackend, remote_path: str = "vault.enc"):
        self.backend = backend
        self.remote_path = remote_path

    def push(self, local_path: str) -> bool:
        """Push local encrypted vault file to remote backend."""
        path = Path(local_path)
        if not path.exists():
            return False
        data = path.read_bytes()
        self.backend.push(data, self.remote_path)
        return True

    def pull(self, local_path: str) -> bool:
        """Pull encrypted vault file from remote backend to local path."""
        data = self.backend.pull(self.remote_path)
        if data is None:
            return False
        path = Path(local_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return True

    def remote_exists(self) -> bool:
        """Check whether a remote vault file exists."""
        return self.backend.exists(self.remote_path)
