"""Tests for envault.env_priority."""

from __future__ import annotations

import pytest

from envault.env_priority import PriorityError, PriorityManager


@pytest.fixture()
def mgr(tmp_path):
    return PriorityManager(str(tmp_path))


class TestPriorityManager:
    def test_list_all_empty_initially(self, mgr):
        assert mgr.list_all() == {}

    def test_set_and_get_priority(self, mgr):
        mgr.set_priority("API_KEY", "high")
        assert mgr.get_priority("API_KEY") == "high"

    def test_set_persists_to_disk(self, tmp_path):
        mgr1 = PriorityManager(str(tmp_path))
        mgr1.set_priority("DB_PASS", "critical")
        mgr2 = PriorityManager(str(tmp_path))
        assert mgr2.get_priority("DB_PASS") == "critical"

    def test_invalid_level_raises(self, mgr):
        with pytest.raises(PriorityError, match="Invalid priority"):
            mgr.set_priority("KEY", "ultra")

    def test_remove_priority(self, mgr):
        mgr.set_priority("FOO", "low")
        mgr.remove_priority("FOO")
        assert mgr.get_priority("FOO") is None

    def test_remove_nonexistent_raises(self, mgr):
        with pytest.raises(PriorityError, match="no priority set"):
            mgr.remove_priority("MISSING")

    def test_get_priority_returns_none_for_unknown(self, mgr):
        assert mgr.get_priority("UNKNOWN") is None

    def test_list_by_level(self, mgr):
        mgr.set_priority("A", "high")
        mgr.set_priority("B", "normal")
        mgr.set_priority("C", "high")
        result = mgr.list_by_level("high")
        assert sorted(result) == ["A", "C"]

    def test_list_by_level_empty_when_none_set(self, mgr):
        assert mgr.list_by_level("critical") == []

    def test_list_by_invalid_level_raises(self, mgr):
        with pytest.raises(PriorityError, match="Invalid priority"):
            mgr.list_by_level("mega")

    def test_list_all_returns_all_entries(self, mgr):
        mgr.set_priority("X", "low")
        mgr.set_priority("Y", "normal")
        assert mgr.list_all() == {"X": "low", "Y": "normal"}

    def test_overwrite_priority(self, mgr):
        mgr.set_priority("KEY", "low")
        mgr.set_priority("KEY", "critical")
        assert mgr.get_priority("KEY") == "critical"
