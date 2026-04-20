"""Tests for envault.env_required."""

from __future__ import annotations

import pytest

from envault.env_required import RequiredError, RequiredManager


@pytest.fixture()
def mgr(tmp_path):
    return RequiredManager(tmp_path)


class TestRequiredManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_required() == []

    def test_mark_required_persists(self, mgr, tmp_path):
        mgr.mark_required("DATABASE_URL")
        mgr2 = RequiredManager(tmp_path)
        assert "DATABASE_URL" in mgr2.list_required()

    def test_mark_duplicate_raises(self, mgr):
        mgr.mark_required("API_KEY")
        with pytest.raises(RequiredError, match="already marked"):
            mgr.mark_required("API_KEY")

    def test_unmark_required(self, mgr):
        mgr.mark_required("SECRET")
        mgr.unmark_required("SECRET")
        assert "SECRET" not in mgr.list_required()

    def test_unmark_nonexistent_raises(self, mgr):
        with pytest.raises(RequiredError, match="not marked"):
            mgr.unmark_required("GHOST")

    def test_is_required_true(self, mgr):
        mgr.mark_required("PORT")
        assert mgr.is_required("PORT") is True

    def test_is_required_false(self, mgr):
        assert mgr.is_required("MISSING") is False

    def test_list_returns_sorted(self, mgr):
        mgr.mark_required("Z_KEY")
        mgr.mark_required("A_KEY")
        mgr.mark_required("M_KEY")
        assert mgr.list_required() == ["A_KEY", "M_KEY", "Z_KEY"]

    def test_validate_no_missing(self, mgr):
        mgr.mark_required("FOO")
        mgr.mark_required("BAR")
        missing = mgr.validate(["FOO", "BAR", "BAZ"])
        assert missing == []

    def test_validate_reports_missing(self, mgr):
        mgr.mark_required("FOO")
        mgr.mark_required("BAR")
        missing = mgr.validate(["FOO"])
        assert missing == ["BAR"]

    def test_validate_empty_vault(self, mgr):
        mgr.mark_required("FOO")
        missing = mgr.validate([])
        assert "FOO" in missing

    def test_no_required_always_passes_validation(self, mgr):
        assert mgr.validate([]) == []
        assert mgr.validate(["ANY", "KEYS"]) == []
