"""Tests for envault.sharing."""

import json
import pytest
from pathlib import Path
from envault.sharing import SharingManager, SharingError


class FakeVault:
    def __init__(self, data=None):
        self._data = data or {}

    def get_all(self):
        return dict(self._data)

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value


@pytest.fixture
def vault():
    return FakeVault({"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "s3cr3t"})


@pytest.fixture
def mgr(vault):
    return SharingManager(vault)


class TestSharingManager:
    def test_create_share_returns_bundle(self, mgr):
        bundle = mgr.create_share(["DB_HOST", "DB_PORT"], "share-pass")
        assert bundle["version"] == 1
        assert "salt" in bundle
        assert "data" in bundle

    def test_create_share_missing_key_raises(self, mgr):
        with pytest.raises(SharingError, match="Keys not found"):
            mgr.create_share(["DB_HOST", "MISSING_KEY"], "pass")

    def test_apply_share_roundtrip(self, mgr):
        bundle = mgr.create_share(["DB_HOST", "SECRET"], "share-pass")
        target = FakeVault()
        target_mgr = SharingManager(target)
        imported = target_mgr.apply_share(bundle, "share-pass")
        assert set(imported) == {"DB_HOST", "SECRET"}
        assert target.get("DB_HOST") == "localhost"
        assert target.get("SECRET") == "s3cr3t"

    def test_apply_share_wrong_password_raises(self, mgr):
        bundle = mgr.create_share(["DB_HOST"], "correct-pass")
        target_mgr = SharingManager(FakeVault())
        with pytest.raises(SharingError, match="Decryption failed"):
            target_mgr.apply_share(bundle, "wrong-pass")

    def test_apply_share_no_overwrite_skips_existing(self, mgr):
        bundle = mgr.create_share(["DB_HOST"], "pass")
        target = FakeVault({"DB_HOST": "original"})
        target_mgr = SharingManager(target)
        imported = target_mgr.apply_share(bundle, "pass", overwrite=False)
        assert imported == []
        assert target.get("DB_HOST") == "original"

    def test_apply_share_overwrite_replaces_existing(self, mgr):
        bundle = mgr.create_share(["DB_HOST"], "pass")
        target = FakeVault({"DB_HOST": "original"})
        target_mgr = SharingManager(target)
        imported = target_mgr.apply_share(bundle, "pass", overwrite=True)
        assert "DB_HOST" in imported
        assert target.get("DB_HOST") == "localhost"

    def test_save_and_load_share(self, mgr, tmp_path):
        bundle = mgr.create_share(["DB_PORT"], "pass")
        out = str(tmp_path / "share.json")
        mgr.save_share(bundle, out)
        loaded = mgr.load_share(out)
        assert loaded == bundle

    def test_load_share_missing_file_raises(self, mgr, tmp_path):
        with pytest.raises(SharingError, match="Share file not found"):
            mgr.load_share(str(tmp_path / "nonexistent.json"))

    def test_apply_share_unsupported_version_raises(self, mgr):
        bundle = mgr.create_share(["DB_HOST"], "pass")
        bundle["version"] = 99
        target_mgr = SharingManager(FakeVault())
        with pytest.raises(SharingError, match="Unsupported bundle version"):
            target_mgr.apply_share(bundle, "pass")

    def test_create_share_empty_keys_raises(self, mgr):
        with pytest.raises(SharingError, match="No keys specified"):
            mgr.create_share([], "pass")
