"""Tests for envault.search module."""

from __future__ import annotations

import pytest

from envault.search import SearchError, SearchManager


class FakeVault:
    """Minimal vault stub for testing."""

    def __init__(self, data: dict) -> None:
        self._data = data

    def get_all(self) -> dict:
        return dict(self._data)


@pytest.fixture
def manager():
    data = {
        "DATABASE_URL": "postgres://localhost/db",
        "DATABASE_POOL": "10",
        "REDIS_URL": "redis://localhost:6379",
        "SECRET_KEY": "supersecret",
        "DEBUG": "true",
    }
    return SearchManager(FakeVault(data))


class TestSearchManager:
    def test_glob_search_matches_prefix_wildcard(self, manager):
        results = manager.search("DATABASE_*", mode="glob")
        assert set(results.keys()) == {"DATABASE_URL", "DATABASE_POOL"}

    def test_glob_search_no_match(self, manager):
        results = manager.search("NONEXISTENT_*", mode="glob")
        assert results == {}

    def test_prefix_search(self, manager):
        results = manager.search("REDIS", mode="prefix")
        assert set(results.keys()) == {"REDIS_URL"}

    def test_regex_search(self, manager):
        results = manager.search(r"^(DATABASE|REDIS)_URL$", mode="regex")
        assert set(results.keys()) == {"DATABASE_URL", "REDIS_URL"}

    def test_regex_invalid_pattern_raises(self, manager):
        with pytest.raises(SearchError, match="Invalid regex"):
            manager.search("[invalid", mode="regex")

    def test_unknown_mode_raises(self, manager):
        with pytest.raises(SearchError, match="Unknown search mode"):
            manager.search("*", mode="fuzzy")

    def test_filter_by_value(self, manager):
        results = manager.filter_by_value("localhost")
        assert set(results.keys()) == {"DATABASE_URL", "REDIS_URL"}

    def test_filter_by_value_no_match(self, manager):
        results = manager.filter_by_value("nowhere")
        assert results == {}

    def test_list_keys_all(self, manager):
        keys = manager.list_keys()
        assert keys == sorted(["DATABASE_URL", "DATABASE_POOL", "REDIS_URL", "SECRET_KEY", "DEBUG"])

    def test_list_keys_with_prefix(self, manager):
        keys = manager.list_keys(prefix="DATABASE")
        assert set(keys) == {"DATABASE_URL", "DATABASE_POOL"}

    def test_list_keys_prefix_no_match(self, manager):
        keys = manager.list_keys(prefix="MISSING")
        assert keys == []
