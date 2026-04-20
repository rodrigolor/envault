"""Tests for OwnershipManager."""

import pytest
from pathlib import Path
from envault.env_ownership import OwnershipManager, OwnershipError


@pytest.fixture
def mgr(tmp_path):
    return OwnershipManager(str(tmp_path))


class TestOwnershipManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_owned() == {}

    def test_assign_and_get_owner(self, mgr):
        mgr.assign("DB_PASSWORD", "alice")
        assert mgr.get_owner("DB_PASSWORD") == "alice"

    def test_assign_persists_to_disk(self, tmp_path):
        mgr = OwnershipManager(str(tmp_path))
        mgr.assign("API_KEY", "bob")
        mgr2 = OwnershipManager(str(tmp_path))
        assert mgr2.get_owner("API_KEY") == "bob"

    def test_get_owner_returns_none_for_unknown_key(self, mgr):
        assert mgr.get_owner("MISSING") is None

    def test_unassign_removes_record(self, mgr):
        mgr.assign("SECRET", "charlie")
        mgr.unassign("SECRET")
        assert mgr.get_owner("SECRET") is None

    def test_unassign_unknown_key_raises(self, mgr):
        with pytest.raises(OwnershipError, match="No ownership record"):
            mgr.unassign("NONEXISTENT")

    def test_list_owned_returns_all(self, mgr):
        mgr.assign("KEY_A", "alice")
        mgr.assign("KEY_B", "bob")
        result = mgr.list_owned()
        assert result == {"KEY_A": "alice", "KEY_B": "bob"}

    def test_owned_by_filters_correctly(self, mgr):
        mgr.assign("KEY_A", "alice")
        mgr.assign("KEY_B", "bob")
        mgr.assign("KEY_C", "alice")
        assert sorted(mgr.owned_by("alice")) == ["KEY_A", "KEY_C"]
        assert mgr.owned_by("bob") == ["KEY_B"]

    def test_owned_by_unknown_owner_returns_empty(self, mgr):
        mgr.assign("KEY_A", "alice")
        assert mgr.owned_by("nobody") == []

    def test_transfer_updates_owner(self, mgr):
        mgr.assign("DB_URL", "alice")
        mgr.transfer("DB_URL", "bob")
        assert mgr.get_owner("DB_URL") == "bob"

    def test_transfer_persists_to_disk(self, tmp_path):
        mgr = OwnershipManager(str(tmp_path))
        mgr.assign("DB_URL", "alice")
        mgr.transfer("DB_URL", "carol")
        mgr2 = OwnershipManager(str(tmp_path))
        assert mgr2.get_owner("DB_URL") == "carol"

    def test_transfer_unknown_key_raises(self, mgr):
        with pytest.raises(OwnershipError, match="No ownership record"):
            mgr.transfer("MISSING", "alice")

    def test_assign_empty_key_raises(self, mgr):
        with pytest.raises(OwnershipError, match="Key must not be empty"):
            mgr.assign("", "alice")

    def test_assign_empty_owner_raises(self, mgr):
        with pytest.raises(OwnershipError, match="Owner must not be empty"):
            mgr.assign("MY_KEY", "")
