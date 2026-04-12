"""Tests for RenameManager."""

import pytest
from envault.env_rename import RenameManager, RenameError


class FakeVault:
    def __init__(self, data=None):
        self._data = dict(data or {})
        self._deleted = []

    def get_all(self):
        return dict(self._data)

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value

    def delete(self, key):
        self._data.pop(key, None)
        self._deleted.append(key)


@pytest.fixture
def vault():
    return FakeVault({"DB_HOST": "localhost", "DB_PORT": "5432"})


@pytest.fixture
def manager(vault):
    return RenameManager(vault)


class TestRenameManager:
    def test_rename_succeeds(self, vault, manager):
        manager.rename("DB_HOST", "DATABASE_HOST")
        assert vault.get("DATABASE_HOST") == "localhost"
        assert vault.get("DB_HOST") is None

    def test_rename_nonexistent_key_raises(self, manager):
        with pytest.raises(RenameError, match="does not exist"):
            manager.rename("MISSING_KEY", "NEW_KEY")

    def test_rename_to_existing_key_raises_without_overwrite(self, manager):
        with pytest.raises(RenameError, match="already exists"):
            manager.rename("DB_HOST", "DB_PORT")

    def test_rename_to_existing_key_succeeds_with_overwrite(self, vault, manager):
        manager.rename("DB_HOST", "DB_PORT", overwrite=True)
        assert vault.get("DB_PORT") == "localhost"
        assert vault.get("DB_HOST") is None

    def test_bulk_rename_succeeds(self, vault, manager):
        results = manager.bulk_rename({"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"})
        assert results == {"DB_HOST": "DATABASE_HOST", "DB_PORT": "DATABASE_PORT"}
        assert vault.get("DATABASE_HOST") == "localhost"
        assert vault.get("DATABASE_PORT") == "5432"

    def test_bulk_rename_partial_failure_raises(self, manager):
        with pytest.raises(RenameError, match="Some renames failed"):
            manager.bulk_rename({"MISSING": "NEW_KEY", "DB_HOST": "DATABASE_HOST"})

    def test_preview_rename_safe(self, manager):
        result = manager.preview_rename("DB_HOST", "DATABASE_HOST")
        assert result["safe"] is True
        assert result["value"] == "localhost"
        assert result["issues"] == []

    def test_preview_rename_missing_source(self, manager):
        result = manager.preview_rename("MISSING", "NEW_KEY")
        assert result["safe"] is False
        assert any("does not exist" in i for i in result["issues"])

    def test_preview_rename_target_exists(self, manager):
        result = manager.preview_rename("DB_HOST", "DB_PORT")
        assert result["safe"] is False
        assert result["target_exists"] is True
        assert any("already exists" in i for i in result["issues"])

    def test_preview_does_not_modify_vault(self, vault, manager):
        original = vault.get_all()
        manager.preview_rename("DB_HOST", "DATABASE_HOST")
        assert vault.get_all() == original
