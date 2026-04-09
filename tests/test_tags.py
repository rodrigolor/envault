"""Tests for the TagManager."""

import pytest
from unittest.mock import MagicMock
from envault.tags import TagManager, TagError


class FakeVault:
    """Minimal in-memory vault stub."""

    def __init__(self, initial=None):
        self._store = dict(initial or {})

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value


@pytest.fixture
def vault():
    v = FakeVault({"DB_URL": "postgres://localhost", "API_KEY": "secret"})
    return v


@pytest.fixture
def manager(vault):
    return TagManager(vault)


class TestTagManager:
    def test_tag_adds_tag_to_key(self, manager):
        manager.tag("DB_URL", "database")
        assert "database" in manager.get_tags("DB_URL")

    def test_tag_nonexistent_key_raises(self, manager):
        with pytest.raises(TagError, match="does not exist"):
            manager.tag("MISSING_KEY", "sometag")

    def test_duplicate_tag_not_added_twice(self, manager):
        manager.tag("DB_URL", "database")
        manager.tag("DB_URL", "database")
        assert manager.get_tags("DB_URL").count("database") == 1

    def test_untag_removes_tag(self, manager):
        manager.tag("DB_URL", "database")
        manager.untag("DB_URL", "database")
        assert "database" not in manager.get_tags("DB_URL")

    def test_untag_nonexistent_tag_raises(self, manager):
        with pytest.raises(TagError, match="not found"):
            manager.untag("DB_URL", "ghost")

    def test_find_by_tag_returns_matching_keys(self, manager):
        manager.tag("DB_URL", "infra")
        manager.tag("API_KEY", "infra")
        result = manager.find_by_tag("infra")
        assert "DB_URL" in result
        assert "API_KEY" in result

    def test_find_by_tag_no_matches(self, manager):
        result = manager.find_by_tag("nonexistent")
        assert result == []

    def test_list_all_tags_returns_sorted_unique(self, manager):
        manager.tag("DB_URL", "zebra")
        manager.tag("API_KEY", "alpha")
        manager.tag("DB_URL", "alpha")
        tags = manager.list_all_tags()
        assert tags == sorted(set(tags))
        assert "alpha" in tags
        assert "zebra" in tags

    def test_get_tags_empty_for_untagged_key(self, manager):
        assert manager.get_tags("DB_URL") == []
