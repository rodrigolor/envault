"""Tests for envault/env_copy.py"""

import pytest
from envault.env_copy import CopyError, EnvCopier


class FakeVault:
    def __init__(self, initial=None):
        self._data = dict(initial or {})

    def get_all(self):
        return dict(self._data)

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value


@pytest.fixture
def vault():
    return FakeVault({"DB_HOST": "localhost", "DB_PORT": "5432"})


@pytest.fixture
def copier(vault):
    return EnvCopier(vault)


class TestEnvCopier:
    def test_copy_creates_dest_key(self, copier, vault):
        copier.copy("DB_HOST", "DB_HOST_BACKUP")
        assert vault.get("DB_HOST_BACKUP") == "localhost"

    def test_copy_preserves_source(self, copier, vault):
        copier.copy("DB_HOST", "DB_HOST_BACKUP")
        assert vault.get("DB_HOST") == "localhost"

    def test_copy_missing_source_raises(self, copier):
        with pytest.raises(CopyError, match="Source key 'MISSING' does not exist"):
            copier.copy("MISSING", "NEW_KEY")

    def test_copy_existing_dest_without_overwrite_raises(self, copier):
        with pytest.raises(CopyError, match="already exists"):
            copier.copy("DB_HOST", "DB_PORT")

    def test_copy_existing_dest_with_overwrite(self, copier, vault):
        copier.copy("DB_HOST", "DB_PORT", overwrite=True)
        assert vault.get("DB_PORT") == "localhost"

    def test_bulk_copy_all_succeed(self, copier, vault):
        results = copier.bulk_copy({"DB_HOST": "DB_HOST_BK", "DB_PORT": "DB_PORT_BK"})
        assert results["DB_HOST_BK"] == "copied"
        assert results["DB_PORT_BK"] == "copied"
        assert vault.get("DB_HOST_BK") == "localhost"
        assert vault.get("DB_PORT_BK") == "5432"

    def test_bulk_copy_skips_existing_without_overwrite(self, copier, vault):
        results = copier.bulk_copy({"DB_HOST": "DB_PORT"})
        assert results["DB_PORT"] == "skipped"
        assert vault.get("DB_PORT") == "5432"  # unchanged

    def test_bulk_copy_missing_source_raises(self, copier):
        with pytest.raises(CopyError, match="Source key 'NOPE' does not exist"):
            copier.bulk_copy({"NOPE": "DEST"})

    def test_duplicate_creates_suffixed_key(self, copier, vault):
        new_key = copier.duplicate("DB_HOST")
        assert new_key == "DB_HOST_COPY"
        assert vault.get("DB_HOST_COPY") == "localhost"

    def test_duplicate_avoids_collision(self, copier, vault):
        vault.set("DB_HOST_COPY", "other")
        new_key = copier.duplicate("DB_HOST")
        assert new_key == "DB_HOST_COPY_1"
        assert vault.get("DB_HOST_COPY_1") == "localhost"

    def test_duplicate_missing_key_raises(self, copier):
        with pytest.raises(CopyError, match="Key 'GHOST' does not exist"):
            copier.duplicate("GHOST")

    def test_duplicate_custom_suffix(self, copier, vault):
        new_key = copier.duplicate("DB_PORT", suffix="_BAK")
        assert new_key == "DB_PORT_BAK"
        assert vault.get("DB_PORT_BAK") == "5432"
