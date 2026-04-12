"""Tests for envault.env_sort."""

import pytest

from envault.env_sort import EnvSorter, SortError


class FakeVault:
    def __init__(self, data):
        self._data = data

    def get_all(self):
        return dict(self._data)


@pytest.fixture()
def vault():
    return FakeVault(
        {
            "DB_HOST": "localhost",
            "APP_ENV": "production",
            "ZEBRA": "stripes",
            "A": "short",
            "DATABASE_URL": "postgres://",
        }
    )


@pytest.fixture()
def sorter(vault):
    return EnvSorter(vault)


class TestEnvSorter:
    def test_alpha_sort_is_ascending(self, sorter):
        keys = sorter.sorted_keys("alpha")
        assert keys == sorted(keys)

    def test_alpha_desc_sort_is_descending(self, sorter):
        keys = sorter.sorted_keys("alpha_desc")
        assert keys == sorted(keys, reverse=True)

    def test_length_sort_shortest_first(self, sorter):
        keys = sorter.sorted_keys("length")
        lengths = [len(k) for k in keys]
        assert lengths == sorted(lengths)

    def test_length_desc_sort_longest_first(self, sorter):
        keys = sorter.sorted_keys("length_desc")
        lengths = [len(k) for k in keys]
        assert lengths == sorted(lengths, reverse=True)

    def test_sort_returns_all_keys(self, sorter, vault):
        result = sorter.sort("alpha")
        assert set(result.keys()) == set(vault.get_all().keys())

    def test_sort_preserves_values(self, sorter, vault):
        result = sorter.sort("alpha")
        for key, value in vault.get_all().items():
            assert result[key] == value

    def test_unknown_mode_raises(self, sorter):
        with pytest.raises(SortError, match="Unknown sort mode"):
            sorter.sort("nonexistent")

    def test_group_by_prefix_default_separator(self, sorter):
        groups = sorter.group_by_prefix()
        assert "DB" in groups
        assert "APP" in groups
        assert "DATABASE" in groups
        assert "DB_HOST" in groups["DB"]

    def test_group_by_prefix_key_without_separator(self, sorter):
        groups = sorter.group_by_prefix()
        # 'ZEBRA' and 'A' have no '_' so they are their own prefix
        assert "ZEBRA" in groups
        assert "A" in groups

    def test_group_by_prefix_custom_separator(self):
        vault = FakeVault({"NS.KEY": "1", "NS.OTHER": "2", "PLAIN": "3"})
        sorter = EnvSorter(vault)
        groups = sorter.group_by_prefix(".")
        assert "NS" in groups
        assert len(groups["NS"]) == 2

    def test_empty_vault_returns_empty_sort(self):
        sorter = EnvSorter(FakeVault({}))
        assert sorter.sort("alpha") == {}
        assert sorter.group_by_prefix() == {}
