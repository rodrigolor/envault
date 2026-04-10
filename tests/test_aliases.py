"""Unit tests for envault.aliases."""

from __future__ import annotations

import pytest

from envault.aliases import AliasError, AliasManager


@pytest.fixture()
def mgr(tmp_path):
    return AliasManager(tmp_path)


class TestAliasManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_aliases() == {}

    def test_add_and_resolve(self, mgr):
        mgr.add("db", "DATABASE_URL")
        assert mgr.resolve("db") == "DATABASE_URL"

    def test_add_persists_to_disk(self, tmp_path):
        mgr1 = AliasManager(tmp_path)
        mgr1.add("token", "API_TOKEN")
        mgr2 = AliasManager(tmp_path)
        assert mgr2.resolve("token") == "API_TOKEN"

    def test_add_duplicate_raises(self, mgr):
        mgr.add("db", "DATABASE_URL")
        with pytest.raises(AliasError, match="already exists"):
            mgr.add("db", "OTHER_KEY")

    def test_add_empty_alias_raises(self, mgr):
        with pytest.raises(AliasError):
            mgr.add("", "SOME_KEY")

    def test_add_empty_key_raises(self, mgr):
        with pytest.raises(AliasError):
            mgr.add("myalias", "")

    def test_remove_existing(self, mgr):
        mgr.add("db", "DATABASE_URL")
        mgr.remove("db")
        assert mgr.resolve("db") is None

    def test_remove_nonexistent_raises(self, mgr):
        with pytest.raises(AliasError, match="not found"):
            mgr.remove("ghost")

    def test_resolve_unknown_returns_none(self, mgr):
        assert mgr.resolve("unknown") is None

    def test_list_aliases_returns_all(self, mgr):
        mgr.add("db", "DATABASE_URL")
        mgr.add("secret", "SECRET_KEY")
        result = mgr.list_aliases()
        assert result == {"db": "DATABASE_URL", "secret": "SECRET_KEY"}

    def test_rename_success(self, mgr):
        mgr.add("db", "DATABASE_URL")
        mgr.rename("db", "database")
        assert mgr.resolve("database") == "DATABASE_URL"
        assert mgr.resolve("db") is None

    def test_rename_old_not_found_raises(self, mgr):
        with pytest.raises(AliasError, match="not found"):
            mgr.rename("ghost", "new")

    def test_rename_new_already_exists_raises(self, mgr):
        mgr.add("db", "DATABASE_URL")
        mgr.add("database", "DATABASE_URL")
        with pytest.raises(AliasError, match="already exists"):
            mgr.rename("db", "database")
