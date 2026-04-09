"""Vault locking mechanism to prevent concurrent access and support auto-lock on timeout."""

import os
import time
import json
from pathlib import Path


class LockError(Exception):
    """Raised when a locking operation fails."""


class VaultLock:
    """Manages a lock file for a vault to prevent concurrent modifications."""

    LOCK_FILENAME = ".vault.lock"
    DEFAULT_TIMEOUT = 300  # seconds (5 minutes)

    def __init__(self, vault_dir: str | Path, timeout: int = DEFAULT_TIMEOUT):
        self.vault_dir = Path(vault_dir)
        self.lock_file = self.vault_dir / self.LOCK_FILENAME
        self.timeout = timeout

    def _read_lock(self) -> dict | None:
        if not self.lock_file.exists():
            return None
        try:
            data = json.loads(self.lock_file.read_text())
            return data
        except (json.JSONDecodeError, OSError):
            return None

    def acquire(self) -> None:
        """Acquire the vault lock. Raises LockError if already locked by another process."""
        existing = self._read_lock()
        if existing is not None:
            acquired_at = existing.get("acquired_at", 0)
            pid = existing.get("pid")
            age = time.time() - acquired_at
            if age < self.timeout:
                raise LockError(
                    f"Vault is locked by PID {pid} (acquired {int(age)}s ago). "
                    f"Lock expires in {int(self.timeout - age)}s."
                )
            # Stale lock — remove it
            self.lock_file.unlink(missing_ok=True)

        self.vault_dir.mkdir(parents=True, exist_ok=True)
        lock_data = {"pid": os.getpid(), "acquired_at": time.time()}
        self.lock_file.write_text(json.dumps(lock_data))

    def release(self) -> None:
        """Release the vault lock if owned by the current process."""
        existing = self._read_lock()
        if existing is None:
            return
        if existing.get("pid") != os.getpid():
            raise LockError(
                f"Cannot release lock owned by PID {existing.get('pid')}."
            )
        self.lock_file.unlink(missing_ok=True)

    def is_locked(self) -> bool:
        """Return True if the vault is currently locked (and lock is not stale)."""
        existing = self._read_lock()
        if existing is None:
            return False
        age = time.time() - existing.get("acquired_at", 0)
        return age < self.timeout

    def __enter__(self) -> "VaultLock":
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()
