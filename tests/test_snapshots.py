"""Tests for envault.snapshots."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.snapshots import SnapshotError, SnapshotManager


class FakeVault:
    def __init__(self, data: dict | None = None):
        self._data: dict = data or {}

    def get_all(self) -> dict:
        return dict(self._data)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def get(self, key: str):
        return self._data.get(key)


@pytest.fixture
def vault() -> FakeVault:
    return FakeVault({"DB_URL": "postgres://localhost", "SECRET": "abc123"})


@pytest.fixture
def mgr(tmp_path: Path, vault: FakeVault) -> SnapshotManager:
    return SnapshotManager(vault, tmp_path)


class TestSnapshotManager:
    def test_create_and_list(self, mgr: SnapshotManager) -> None:
        mgr.create("v1")
        snapshots = mgr.list_snapshots()
        assert len(snapshots) == 1
        assert snapshots[0]["name"] == "v1"
        assert snapshots[0]["count"] == 2

    def test_create_duplicate_raises(self, mgr: SnapshotManager) -> None:
        mgr.create("v1")
        with pytest.raises(SnapshotError, match="already exists"):
            mgr.create("v1")

    def test_get_returns_variables(self, mgr: SnapshotManager, vault: FakeVault) -> None:
        mgr.create("v1")
        variables = mgr.get("v1")
        assert variables == {"DB_URL": "postgres://localhost", "SECRET": "abc123"}

    def test_get_nonexistent_returns_none(self, mgr: SnapshotManager) -> None:
        assert mgr.get("ghost") is None

    def test_restore_applies_variables(self, mgr: SnapshotManager, vault: FakeVault) -> None:
        mgr.create("v1")
        vault.set("DB_URL", "changed")
        count = mgr.restore("v1")
        assert count == 2
        assert vault.get("DB_URL") == "postgres://localhost"

    def test_restore_nonexistent_raises(self, mgr: SnapshotManager) -> None:
        with pytest.raises(SnapshotError, match="not found"):
            mgr.restore("missing")

    def test_delete_removes_snapshot(self, mgr: SnapshotManager) -> None:
        mgr.create("v1")
        mgr.delete("v1")
        assert mgr.list_snapshots() == []

    def test_delete_nonexistent_raises(self, mgr: SnapshotManager) -> None:
        with pytest.raises(SnapshotError, match="not found"):
            mgr.delete("nope")

    def test_snapshots_persisted_to_disk(self, tmp_path: Path, vault: FakeVault) -> None:
        mgr1 = SnapshotManager(vault, tmp_path)
        mgr1.create("v1")
        mgr2 = SnapshotManager(vault, tmp_path)
        assert len(mgr2.list_snapshots()) == 1
        assert mgr2.get("v1") == {"DB_URL": "postgres://localhost", "SECRET": "abc123"}
