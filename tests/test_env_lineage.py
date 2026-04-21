"""Tests for envault.env_lineage."""

from __future__ import annotations

import pytest

from envault.env_lineage import LineageError, LineageManager


@pytest.fixture()
def mgr(tmp_path):
    return LineageManager(str(tmp_path))


class TestLineageManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_all() == {}

    def test_record_and_get(self, mgr):
        mgr.record("DB_URL", "manual")
        info = mgr.get("DB_URL")
        assert info is not None
        assert info["origin"] == "manual"
        assert info["derived_from"] is None

    def test_record_with_derived_from(self, mgr):
        mgr.record("DB_URL", "manual")
        mgr.record("DB_URL_REPLICA", "copy", derived_from="DB_URL")
        info = mgr.get("DB_URL_REPLICA")
        assert info["derived_from"] == "DB_URL"

    def test_record_persists_to_disk(self, tmp_path):
        mgr1 = LineageManager(str(tmp_path))
        mgr1.record("SECRET", "import")
        mgr2 = LineageManager(str(tmp_path))
        assert mgr2.get("SECRET")["origin"] == "import"

    def test_get_unknown_key_returns_none(self, mgr):
        assert mgr.get("MISSING") is None

    def test_derived_from_returns_children(self, mgr):
        mgr.record("PARENT", "manual")
        mgr.record("CHILD_A", "copy", derived_from="PARENT")
        mgr.record("CHILD_B", "copy", derived_from="PARENT")
        mgr.record("UNRELATED", "manual")
        children = mgr.derived_from("PARENT")
        assert set(children) == {"CHILD_A", "CHILD_B"}

    def test_derived_from_no_children(self, mgr):
        mgr.record("ORPHAN", "manual")
        assert mgr.derived_from("ORPHAN") == []

    def test_remove_deletes_record(self, mgr):
        mgr.record("API_KEY", "manual")
        mgr.remove("API_KEY")
        assert mgr.get("API_KEY") is None

    def test_remove_unknown_key_raises(self, mgr):
        with pytest.raises(LineageError, match="No lineage record"):
            mgr.remove("GHOST")

    def test_record_empty_key_raises(self, mgr):
        with pytest.raises(LineageError, match="Key must not be empty"):
            mgr.record("", "manual")

    def test_overwrite_existing_record(self, mgr):
        mgr.record("KEY", "manual")
        mgr.record("KEY", "import")
        assert mgr.get("KEY")["origin"] == "import"

    def test_list_all_returns_all_entries(self, mgr):
        mgr.record("A", "manual")
        mgr.record("B", "copy", derived_from="A")
        data = mgr.list_all()
        assert set(data.keys()) == {"A", "B"}
