"""Tests for envault.env_defaults."""

from __future__ import annotations

import pytest

from envault.env_defaults import DefaultsError, DefaultsManager


class FakeVault:
    def __init__(self, data: dict | None = None) -> None:
        self._data: dict = data or {}

    def get_all(self) -> dict:
        return dict(self._data)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def get(self, key: str):
        return self._data.get(key)


@pytest.fixture()
def mgr(tmp_path):
    return DefaultsManager(tmp_path)


class TestDefaultsManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_defaults() == {}

    def test_set_default_persists(self, tmp_path):
        mgr = DefaultsManager(tmp_path)
        mgr.set_default("LOG_LEVEL", "INFO")
        mgr2 = DefaultsManager(tmp_path)
        assert mgr2.get_default("LOG_LEVEL") == "INFO"

    def test_set_and_get_default(self, mgr):
        mgr.set_default("PORT", "8080")
        assert mgr.get_default("PORT") == "8080"

    def test_get_missing_default_returns_none(self, mgr):
        assert mgr.get_default("MISSING") is None

    def test_remove_default(self, mgr):
        mgr.set_default("X", "1")
        mgr.remove_default("X")
        assert mgr.get_default("X") is None

    def test_remove_nonexistent_raises(self, mgr):
        with pytest.raises(DefaultsError, match="No default"):
            mgr.remove_default("GHOST")

    def test_list_defaults_returns_all(self, mgr):
        mgr.set_default("A", "1")
        mgr.set_default("B", "2")
        assert mgr.list_defaults() == {"A": "1", "B": "2"}

    def test_apply_sets_missing_keys(self, mgr):
        vault = FakeVault()
        mgr.set_default("HOST", "localhost")
        mgr.set_default("PORT", "5432")
        applied = mgr.apply(vault)
        assert applied == {"HOST": "localhost", "PORT": "5432"}
        assert vault.get("HOST") == "localhost"

    def test_apply_skips_existing_keys(self, mgr):
        vault = FakeVault({"HOST": "prod.example.com"})
        mgr.set_default("HOST", "localhost")
        applied = mgr.apply(vault)
        assert applied == {}
        assert vault.get("HOST") == "prod.example.com"

    def test_apply_returns_empty_when_no_defaults(self, mgr):
        vault = FakeVault()
        assert mgr.apply(vault) == {}
