"""Storage backend interface and local file implementation."""

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def save(self, data: bytes) -> None:
        """Save encrypted data to storage."""
        pass

    @abstractmethod
    def load(self) -> Optional[bytes]:
        """Load encrypted data from storage."""
        pass

    @abstractmethod
    def exists(self) -> bool:
        """Check if storage contains data."""
        pass

    @abstractmethod
    def delete(self) -> None:
        """Delete data from storage."""
        pass


class LocalFileStorage(StorageBackend):
    """Local file system storage backend."""

    def __init__(self, file_path: Optional[str] = None):
        """Initialize local file storage.
        
        Args:
            file_path: Path to storage file. Defaults to ~/.envault/vault.enc
        """
        if file_path is None:
            home_dir = Path.home()
            self.storage_dir = home_dir / ".envault"
            self.file_path = self.storage_dir / "vault.enc"
        else:
            self.file_path = Path(file_path)
            self.storage_dir = self.file_path.parent

    def save(self, data: bytes) -> None:
        """Save encrypted data to local file."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, 'wb') as f:
            f.write(data)

    def load(self) -> Optional[bytes]:
        """Load encrypted data from local file."""
        if not self.exists():
            return None
        with open(self.file_path, 'rb') as f:
            return f.read()

    def exists(self) -> bool:
        """Check if storage file exists."""
        return self.file_path.exists()

    def delete(self) -> None:
        """Delete storage file."""
        if self.exists():
            self.file_path.unlink()

    def get_path(self) -> str:
        """Get the storage file path as string."""
        return str(self.file_path)
