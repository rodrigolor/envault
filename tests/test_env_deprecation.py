"""Tests for DeprecationManager."""

from __future__ import annotations

import pytest

from envault.env_deprecation import DeprecationManager, DeprecationError


@pytest.fixture
def mgr(tmp_path):
    return DeprecationManager(tmp_path)


class TestDeprecationManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_deprecated() == {}

    def test_mark_deprecated_persists(self, mgr, tmp_path):
        mgr.mark_deprecated("OLD_KEY", reason="Replaced", replacement="NEW_KEY")
        mgr2 = DeprecationManager(tmp_path)
        assert mgr2.is_deprecated("OLD_KEY")

    def test_is_deprecated_false_for_unknown(self, mgr):
        assert not mgr.is_deprecated("UNKNOWN_KEY")

    def test_get_info_returns_none_for_unknown(self, mgr):
        assert mgr.get_info("UNKNOWN") is None

    def test_get_info_returns_dict(self, mgr):
        mgr.mark_deprecated("FOO", reason="old", replacement="BAR")
        info = mgr.get_info("FOO")
        assert info["reason"] == "old"
        assert info["replacement"] == "BAR"

    def test_unmark_removes_key(self, mgr):
        mgr.mark_deprecated("FOO")
        mgr.unmark_deprecated("FOO")
        assert not mgr.is_deprecated("FOO")

    def test_unmark_nonexistent_raises(self, mgr):
        with pytest.raises(DeprecationError, match="not marked"):
            mgr.unmark_deprecated("GHOST")

    def test_mark_empty_key_raises(self, mgr):
        with pytest.raises(DeprecationError, match="empty"):
            mgr.mark_deprecated("")

    def test_warn_if_deprecated_returns_none_for_valid(self, mgr):
        assert mgr.warn_if_deprecated("ACTIVE_KEY") is None

    def test_warn_if_deprecated_includes_reason(self, mgr):
        mgr.mark_deprecated("OLD", reason="too old")
        msg = mgr.warn_if_deprecated("OLD")
        assert "too old" in msg
        assert "OLD" in msg

    def test_warn_if_deprecated_includes_replacement(self, mgr):
        mgr.mark_deprecated("OLD", replacement="NEW")
        msg = mgr.warn_if_deprecated("OLD")
        assert "NEW" in msg

    def test_list_deprecated_returns_all(self, mgr):
        mgr.mark_deprecated("A")
        mgr.mark_deprecated("B", reason="gone")
        result = mgr.list_deprecated()
        assert set(result.keys()) == {"A", "B"}

    def test_mark_overwrites_existing(self, mgr):
        mgr.mark_deprecated("KEY", reason="v1")
        mgr.mark_deprecated("KEY", reason="v2")
        assert mgr.get_info("KEY")["reason"] == "v2"
