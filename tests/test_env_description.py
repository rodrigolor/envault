"""Tests for DescriptionManager."""

import pytest
from pathlib import Path
from envault.env_description import DescriptionManager, DescriptionError


@pytest.fixture
def mgr(tmp_path):
    return DescriptionManager(str(tmp_path))


class TestDescriptionManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_all() == {}

    def test_set_and_get(self, mgr):
        mgr.set("DATABASE_URL", "Primary database connection string")
        assert mgr.get("DATABASE_URL") == "Primary database connection string"

    def test_set_persists_to_disk(self, tmp_path):
        mgr = DescriptionManager(str(tmp_path))
        mgr.set("API_KEY", "Third-party API key")
        mgr2 = DescriptionManager(str(tmp_path))
        assert mgr2.get("API_KEY") == "Third-party API key"

    def test_get_nonexistent_returns_none(self, mgr):
        assert mgr.get("MISSING") is None

    def test_remove_existing(self, mgr):
        mgr.set("FOO", "bar")
        mgr.remove("FOO")
        assert mgr.get("FOO") is None

    def test_remove_nonexistent_raises(self, mgr):
        with pytest.raises(DescriptionError, match="No description found"):
            mgr.remove("GHOST")

    def test_set_empty_key_raises(self, mgr):
        with pytest.raises(DescriptionError, match="Key must not be empty"):
            mgr.set("", "some desc")

    def test_overwrite_description(self, mgr):
        mgr.set("KEY", "old")
        mgr.set("KEY", "new")
        assert mgr.get("KEY") == "new"

    def test_annotate_filters_to_vault_keys(self, mgr):
        mgr.set("A", "desc A")
        mgr.set("B", "desc B")
        result = mgr.annotate(["A", "C"])
        assert result == {"A": "desc A", "C": ""}

    def test_list_returns_all(self, mgr):
        mgr.set("X", "x desc")
        mgr.set("Y", "y desc")
        assert mgr.list_all() == {"X": "x desc", "Y": "y desc"}
