"""Tests for key rotation functionality."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.crypto import CryptoManager
from envault.storage import LocalStorageBackend
from envault.rotation import KeyRotationManager, RotationError


@pytest.fixture
def vault_dir(tmp_path: Path) -> Path:
    """Create a minimal encrypted vault for testing."""
    old_password = "old-secret"
    data = {"API_KEY": "abc123", "DB_URL": "postgres://localhost/test"}
    crypto = CryptoManager(old_password)
    ciphertext = crypto.encrypt(json.dumps(data))
    storage = LocalStorageBackend(tmp_path)
    storage.save(ciphertext)
    return tmp_path


class TestKeyRotationManager:
    def test_rotate_succeeds_with_correct_old_password(self, vault_dir):
        mgr = KeyRotationManager(vault_dir)
        count = mgr.rotate("old-secret", "new-secret")
        assert count == 2

    def test_rotate_new_password_decrypts_correctly(self, vault_dir):
        mgr = KeyRotationManager(vault_dir)
        mgr.rotate("old-secret", "new-secret")

        storage = LocalStorageBackend(vault_dir)
        raw = storage.load()
        new_crypto = CryptoManager("new-secret")
        plaintext = new_crypto.decrypt(raw)
        data = json.loads(plaintext)
        assert data["API_KEY"] == "abc123"

    def test_rotate_old_password_no_longer_works(self, vault_dir):
        mgr = KeyRotationManager(vault_dir)
        mgr.rotate("old-secret", "new-secret")

        storage = LocalStorageBackend(vault_dir)
        raw = storage.load()
        old_crypto = CryptoManager("old-secret")
        with pytest.raises(Exception):
            old_crypto.decrypt(raw)

    def test_rotate_wrong_old_password_raises(self, vault_dir):
        mgr = KeyRotationManager(vault_dir)
        with pytest.raises(RotationError, match="Failed to decrypt"):
            mgr.rotate("wrong-password", "new-secret")

    def test_rotate_missing_vault_raises(self, tmp_path):
        mgr = KeyRotationManager(tmp_path / "nonexistent")
        with pytest.raises(RotationError, match="does not exist"):
            mgr.rotate("old", "new")

    def test_needs_rotation_returns_true_when_no_audit(self, tmp_path):
        mgr = KeyRotationManager(tmp_path)
        assert mgr.needs_rotation("") is True

    def test_needs_rotation_false_after_recent_rotation(self, vault_dir):
        mgr = KeyRotationManager(vault_dir)
        mgr.rotate("old-secret", "new-secret")
        assert mgr.needs_rotation("", max_age_days=90) is False
