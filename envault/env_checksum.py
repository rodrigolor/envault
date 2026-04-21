"""Checksum manager for detecting tampering or unexpected changes in vault values."""

import hashlib
import json
from pathlib import Path
from typing import Dict, Optional


class ChecksumError(Exception):
    pass


class ChecksumManager:
    FILENAME = "checksums.json"

    def __init__(self, vault_dir: str):
        self._path = Path(vault_dir) / self.FILENAME
        self._data: Dict[str, str] = self._load()

    def _load(self) -> Dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    @staticmethod
    def _hash(value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def record(self, key: str, value: str) -> str:
        """Record a checksum for the given key/value pair."""
        digest = self._hash(value)
        self._data[key] = digest
        self._save()
        return digest

    def verify(self, key: str, value: str) -> bool:
        """Return True if the value matches the recorded checksum."""
        if key not in self._data:
            raise ChecksumError(f"No checksum recorded for key: '{key}'")
        return self._data[key] == self._hash(value)

    def remove(self, key: str) -> None:
        """Remove the checksum entry for a key."""
        if key not in self._data:
            raise ChecksumError(f"No checksum recorded for key: '{key}'")
        del self._data[key]
        self._save()

    def list_all(self) -> Dict[str, str]:
        """Return a copy of all recorded checksums."""
        return dict(self._data)

    def has_checksum(self, key: str) -> bool:
        return key in self._data
