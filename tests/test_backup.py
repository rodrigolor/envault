"""Tests for envault.backup module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock

from envault.backup import BackupManager, BackupError


class FakeVault:
    def __init__(self, data=None):
        self._data = data or {}

    def get_all(self):
        return dict(self._data)

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        return self._data.get(key)


@pytest.fixture
def tmp_backup(tmp_path):
    return tmp_path / "backups"


@pytest.fixture
def vault():
    return FakeVault({"DB_URL": "postgres://localhost/db", "SECRET": "abc123"})


@pytest.fixture
def mgr(vault, tmp_backup):
    return BackupManager(vault, tmp_backup)


class TestBackupManager:
    def test_create_returns_zip_path(self, mgr, tmp_backup):
        path = mgr.create()
        assert path.suffix == ".zip"
        assert path.parent == tmp_backup

    def test_create_with_label_includes_label_in_filename(self, mgr):
        path = mgr.create(label="prod")
        assert "prod" in path.name

    def test_backup_dir_created_automatically(self, vault, tmp_path):
        new_dir = tmp_path / "nested" / "backups"
        m = BackupManager(vault, new_dir)
        assert new_dir.exists()

    def test_create_archive_contains_data(self, mgr):
        import zipfile, json
        path = mgr.create()
        with zipfile.ZipFile(path, "r") as zf:
            data = json.loads(zf.read("vault_data.json"))
        assert data["DB_URL"] == "postgres://localhost/db"
        assert data["SECRET"] == "abc123"

    def test_restore_populates_vault(self, mgr, vault, tmp_backup):
        path = mgr.create()
        empty_vault = FakeVault()
        restore_mgr = BackupManager(empty_vault, tmp_backup)
        count = restore_mgr.restore(path)
        assert count == 2
        assert empty_vault.get("DB_URL") == "postgres://localhost/db"

    def test_restore_skips_existing_keys_by_default(self, mgr, tmp_backup):
        path = mgr.create()
        prefilled = FakeVault({"DB_URL": "old_value", "OTHER": "x"})
        restore_mgr = BackupManager(prefilled, tmp_backup)
        count = restore_mgr.restore(path)
        assert count == 1  # only SECRET is new
        assert prefilled.get("DB_URL") == "old_value"

    def test_restore_overwrite_replaces_existing(self, mgr, tmp_backup):
        path = mgr.create()
        prefilled = FakeVault({"DB_URL": "old_value"})
        restore_mgr = BackupManager(prefilled, tmp_backup)
        restore_mgr.restore(path, overwrite=True)
        assert prefilled.get("DB_URL") == "postgres://localhost/db"

    def test_restore_missing_file_raises(self, mgr, tmp_path):
        with pytest.raises(BackupError, match="not found"):
            mgr.restore(tmp_path / "nonexistent.zip")

    def test_list_backups_returns_newest_first(self, mgr):
        p1 = mgr.create(label="first")
        p2 = mgr.create(label="second")
        backups = mgr.list_backups()
        assert backups[0].name >= backups[-1].name
        assert len(backups) == 2

    def test_create_raises_on_vault_error(self, tmp_backup):
        broken = MagicMock()
        broken.get_all.side_effect = RuntimeError("vault locked")
        m = BackupManager(broken, tmp_backup)
        with pytest.raises(BackupError, match="Failed to read vault data"):
            m.create()
