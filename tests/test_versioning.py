"""Tests for envault.versioning."""

from __future__ import annotations

import pytest

from envault.versioning import VersionError, VersionManager


class FakeVault:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def get_all(self) -> dict[str, str]:
        return dict(self._store)

    def set(self, key: str, value: str) -> None:
        self._store[key] = value

    def get(self, key: str) -> str | None:
        return self._store.get(key)


@pytest.fixture()
def mgr(tmp_path):
    return VersionManager(tmp_path)


class TestVersionManager:
    def test_list_versions_empty_initially(self, mgr):
        assert mgr.list_versions("MY_KEY") == []

    def test_record_creates_version_file(self, mgr, tmp_path):
        mgr.record("API_KEY", "secret1")
        assert (tmp_path / "versions.json").exists()

    def test_record_and_list_single_version(self, mgr):
        mgr.record("DB_PASS", "hunter2")
        versions = mgr.list_versions("DB_PASS")
        assert len(versions) == 1
        assert versions[0]["value"] == "hunter2"
        assert "timestamp" in versions[0]

    def test_multiple_versions_ordered_oldest_first(self, mgr):
        for v in ("v1", "v2", "v3"):
            mgr.record("TOKEN", v)
        versions = mgr.list_versions("TOKEN")
        assert [e["value"] for e in versions] == ["v1", "v2", "v3"]

    def test_get_version_by_index(self, mgr):
        mgr.record("X", "alpha")
        mgr.record("X", "beta")
        assert mgr.get_version("X", 0) == "alpha"
        assert mgr.get_version("X", 1) == "beta"

    def test_get_version_invalid_key_raises(self, mgr):
        with pytest.raises(VersionError, match="No version history"):
            mgr.get_version("MISSING", 0)

    def test_get_version_invalid_index_raises(self, mgr):
        mgr.record("K", "val")
        with pytest.raises(VersionError, match="out of range"):
            mgr.get_version("K", 99)

    def test_max_versions_trimmed(self, mgr):
        for i in range(15):
            mgr.record("BIG", f"val{i}")
        versions = mgr.list_versions("BIG")
        assert len(versions) == VersionManager.MAX_VERSIONS
        assert versions[-1]["value"] == "val14"

    def test_rollback_restores_previous_value(self, mgr):
        vault = FakeVault()
        vault.set("PWD", "new")
        mgr.record("PWD", "old")
        mgr.record("PWD", "new")
        restored = mgr.rollback("PWD", vault)
        assert restored == "old"
        assert vault.get("PWD") == "old"

    def test_rollback_insufficient_history_raises(self, mgr):
        vault = FakeVault()
        mgr.record("PWD", "only_one")
        with pytest.raises(VersionError, match="Not enough history"):
            mgr.rollback("PWD", vault)

    def test_clear_removes_history(self, mgr):
        mgr.record("Z", "a")
        mgr.record("Z", "b")
        mgr.clear("Z")
        assert mgr.list_versions("Z") == []

    def test_clear_nonexistent_key_is_noop(self, mgr):
        mgr.clear("DOES_NOT_EXIST")  # should not raise
