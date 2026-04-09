"""Tests for envault.locking — VaultLock."""

import os
import time
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envault.locking import VaultLock, LockError


@pytest.fixture
def vault_dir(tmp_path: Path) -> Path:
    return tmp_path / "vault"


@pytest.fixture
def lock(vault_dir: Path) -> VaultLock:
    return VaultLock(vault_dir, timeout=60)


class TestVaultLock:
    def test_acquire_creates_lock_file(self, lock: VaultLock, vault_dir: Path):
        lock.acquire()
        assert (vault_dir / VaultLock.LOCK_FILENAME).exists()
        lock.release()

    def test_is_locked_false_before_acquire(self, lock: VaultLock):
        assert lock.is_locked() is False

    def test_is_locked_true_after_acquire(self, lock: VaultLock):
        lock.acquire()
        assert lock.is_locked() is True
        lock.release()

    def test_is_locked_false_after_release(self, lock: VaultLock):
        lock.acquire()
        lock.release()
        assert lock.is_locked() is False

    def test_acquire_raises_if_already_locked(self, vault_dir: Path):
        lock1 = VaultLock(vault_dir, timeout=60)
        lock2 = VaultLock(vault_dir, timeout=60)
        lock1.acquire()
        with pytest.raises(LockError, match="locked by PID"):
            lock2.acquire()
        lock1.release()

    def test_stale_lock_is_overwritten(self, vault_dir: Path):
        """A lock older than the timeout should be treated as stale and overwritten."""
        vault_dir.mkdir(parents=True, exist_ok=True)
        lock_file = vault_dir / VaultLock.LOCK_FILENAME
        stale_data = {"pid": 99999, "acquired_at": time.time() - 400}
        lock_file.write_text(json.dumps(stale_data))

        lock = VaultLock(vault_dir, timeout=300)
        lock.acquire()  # Should not raise
        data = json.loads(lock_file.read_text())
        assert data["pid"] == os.getpid()
        lock.release()

    def test_release_raises_if_owned_by_other_pid(self, vault_dir: Path):
        vault_dir.mkdir(parents=True, exist_ok=True)
        lock_file = vault_dir / VaultLock.LOCK_FILENAME
        lock_file.write_text(json.dumps({"pid": 99999, "acquired_at": time.time()}))

        lock = VaultLock(vault_dir, timeout=60)
        with pytest.raises(LockError, match="Cannot release lock"):
            lock.release()

    def test_context_manager_acquires_and_releases(self, lock: VaultLock):
        with lock:
            assert lock.is_locked() is True
        assert lock.is_locked() is False

    def test_context_manager_releases_on_exception(self, lock: VaultLock):
        try:
            with lock:
                assert lock.is_locked() is True
                raise ValueError("boom")
        except ValueError:
            pass
        assert lock.is_locked() is False
