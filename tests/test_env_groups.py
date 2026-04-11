"""Tests for GroupManager."""

import pytest
from pathlib import Path
from envault.env_groups import GroupManager, GroupError


@pytest.fixture
def mgr(tmp_path):
    return GroupManager(str(tmp_path))


class TestGroupManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_groups() == []

    def test_create_group(self, mgr):
        mgr.create("backend")
        assert "backend" in mgr.list_groups()

    def test_create_duplicate_raises(self, mgr):
        mgr.create("backend")
        with pytest.raises(GroupError, match="already exists"):
            mgr.create("backend")

    def test_delete_group(self, mgr):
        mgr.create("backend")
        mgr.delete("backend")
        assert "backend" not in mgr.list_groups()

    def test_delete_nonexistent_raises(self, mgr):
        with pytest.raises(GroupError, match="does not exist"):
            mgr.delete("ghost")

    def test_add_key_to_group(self, mgr):
        mgr.create("backend")
        mgr.add_key("backend", "DB_HOST")
        assert "DB_HOST" in mgr.get_keys("backend")

    def test_add_duplicate_key_raises(self, mgr):
        mgr.create("backend")
        mgr.add_key("backend", "DB_HOST")
        with pytest.raises(GroupError, match="already in group"):
            mgr.add_key("backend", "DB_HOST")

    def test_add_key_to_nonexistent_group_raises(self, mgr):
        with pytest.raises(GroupError, match="does not exist"):
            mgr.add_key("ghost", "DB_HOST")

    def test_remove_key_from_group(self, mgr):
        mgr.create("backend")
        mgr.add_key("backend", "DB_HOST")
        mgr.remove_key("backend", "DB_HOST")
        assert "DB_HOST" not in mgr.get_keys("backend")

    def test_remove_nonexistent_key_raises(self, mgr):
        mgr.create("backend")
        with pytest.raises(GroupError, match="not in group"):
            mgr.remove_key("backend", "MISSING")

    def test_find_groups_for_key(self, mgr):
        mgr.create("backend")
        mgr.create("frontend")
        mgr.add_key("backend", "API_KEY")
        mgr.add_key("frontend", "API_KEY")
        groups = mgr.find_groups_for_key("API_KEY")
        assert "backend" in groups
        assert "frontend" in groups

    def test_find_groups_for_unknown_key_returns_empty(self, mgr):
        mgr.create("backend")
        assert mgr.find_groups_for_key("NOPE") == []

    def test_persists_to_disk(self, tmp_path):
        m1 = GroupManager(str(tmp_path))
        m1.create("infra")
        m1.add_key("infra", "AWS_KEY")
        m2 = GroupManager(str(tmp_path))
        assert "infra" in m2.list_groups()
        assert "AWS_KEY" in m2.get_keys("infra")
