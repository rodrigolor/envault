"""Tests for NamespaceManager."""

import pytest
from envault.env_namespace import NamespaceManager, NamespaceError


@pytest.fixture
def mgr(tmp_path):
    return NamespaceManager(str(tmp_path))


class TestNamespaceManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_namespaces() == []

    def test_create_namespace(self, mgr):
        mgr.create("app")
        assert "app" in mgr.list_namespaces()

    def test_create_duplicate_raises(self, mgr):
        mgr.create("app")
        with pytest.raises(NamespaceError, match="already exists"):
            mgr.create("app")

    def test_delete_namespace(self, mgr):
        mgr.create("app")
        mgr.delete("app")
        assert "app" not in mgr.list_namespaces()

    def test_delete_nonexistent_raises(self, mgr):
        with pytest.raises(NamespaceError, match="does not exist"):
            mgr.delete("ghost")

    def test_assign_key(self, mgr):
        mgr.create("app")
        mgr.assign("app", "DB_HOST")
        assert "DB_HOST" in mgr.keys_in("app")

    def test_assign_to_nonexistent_namespace_raises(self, mgr):
        with pytest.raises(NamespaceError, match="does not exist"):
            mgr.assign("ghost", "DB_HOST")

    def test_assign_duplicate_is_idempotent(self, mgr):
        mgr.create("app")
        mgr.assign("app", "DB_HOST")
        mgr.assign("app", "DB_HOST")
        assert mgr.keys_in("app").count("DB_HOST") == 1

    def test_unassign_key(self, mgr):
        mgr.create("app")
        mgr.assign("app", "DB_HOST")
        mgr.unassign("app", "DB_HOST")
        assert "DB_HOST" not in mgr.keys_in("app")

    def test_unassign_missing_key_raises(self, mgr):
        mgr.create("app")
        with pytest.raises(NamespaceError, match="not in namespace"):
            mgr.unassign("app", "MISSING")

    def test_namespace_of_returns_correct(self, mgr):
        mgr.create("infra")
        mgr.assign("infra", "AWS_KEY")
        assert mgr.namespace_of("AWS_KEY") == "infra"

    def test_namespace_of_unknown_key_returns_none(self, mgr):
        assert mgr.namespace_of("UNKNOWN") is None

    def test_persists_to_disk(self, tmp_path):
        m1 = NamespaceManager(str(tmp_path))
        m1.create("db")
        m1.assign("db", "DB_URL")
        m2 = NamespaceManager(str(tmp_path))
        assert "db" in m2.list_namespaces()
        assert "DB_URL" in m2.keys_in("db")
