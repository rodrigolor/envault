"""Tests for envault.diff."""

import pytest

from envault.diff import DiffError, DiffManager, DiffResult


class FakeVault:
    def __init__(self, data: dict):
        self._data = data

    def get_all(self) -> dict:
        return dict(self._data)


class BrokenVault:
    def get_all(self):
        raise RuntimeError("storage unavailable")


@pytest.fixture
def vault():
    return FakeVault({"KEY_A": "alpha", "KEY_B": "beta", "KEY_C": "gamma"})


@pytest.fixture
def manager(vault):
    return DiffManager(vault)


class TestDiffResult:
    def test_has_changes_false_when_empty(self):
        result = DiffResult()
        assert not result.has_changes

    def test_has_changes_true_when_added(self):
        result = DiffResult(added={"NEW": "val"})
        assert result.has_changes

    def test_summary_no_changes(self):
        assert DiffResult().summary() == "No changes."

    def test_summary_contains_added_key(self):
        result = DiffResult(added={"X": "1"})
        assert "+ X=1" in result.summary()

    def test_summary_contains_removed_key(self):
        result = DiffResult(removed={"OLD": "gone"})
        assert "- OLD=gone" in result.summary()

    def test_summary_contains_modified_key(self):
        result = DiffResult(modified={"K": ("old", "new")})
        assert "~ K" in result.summary()


class TestDiffManager:
    def test_compare_identical_returns_no_changes(self, manager):
        other = {"KEY_A": "alpha", "KEY_B": "beta", "KEY_C": "gamma"}
        result = manager.compare(other)
        assert not result.has_changes

    def test_compare_detects_added_key(self, manager):
        other = {"KEY_A": "alpha", "KEY_B": "beta"}
        result = manager.compare(other)
        assert "KEY_C" in result.added

    def test_compare_detects_removed_key(self, manager):
        other = {"KEY_A": "alpha", "KEY_B": "beta", "KEY_C": "gamma", "KEY_D": "delta"}
        result = manager.compare(other)
        assert "KEY_D" in result.removed

    def test_compare_detects_modified_key(self, manager):
        other = {"KEY_A": "CHANGED", "KEY_B": "beta", "KEY_C": "gamma"}
        result = manager.compare(other)
        assert "KEY_A" in result.modified
        assert result.modified["KEY_A"] == ("CHANGED", "alpha")

    def test_compare_raises_diff_error_on_vault_failure(self):
        mgr = DiffManager(BrokenVault())
        with pytest.raises(DiffError, match="storage unavailable"):
            mgr.compare({})

    def test_compare_snapshots_no_vault_needed(self):
        mgr = DiffManager(vault=None)
        snap_a = {"A": "1", "B": "2"}
        snap_b = {"A": "1", "C": "3"}
        result = mgr.compare_snapshots(snap_a, snap_b)
        assert "B" in result.removed
        assert "C" in result.added
        assert not result.modified
