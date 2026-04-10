"""Tests for envault.pinning.PinManager."""

from __future__ import annotations

import pytest

from envault.pinning import PinError, PinManager


@pytest.fixture()
def mgr(tmp_path):
    return PinManager(tmp_path)


class TestPinManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_pins() == []

    def test_pin_key(self, mgr):
        mgr.pin("SECRET_KEY")
        assert mgr.is_pinned("SECRET_KEY")

    def test_pin_persists_to_disk(self, tmp_path):
        mgr1 = PinManager(tmp_path)
        mgr1.pin("DB_PASSWORD")
        mgr2 = PinManager(tmp_path)
        assert mgr2.is_pinned("DB_PASSWORD")

    def test_pin_duplicate_raises(self, mgr):
        mgr.pin("API_KEY")
        with pytest.raises(PinError, match="already pinned"):
            mgr.pin("API_KEY")

    def test_unpin_key(self, mgr):
        mgr.pin("TOKEN")
        mgr.unpin("TOKEN")
        assert not mgr.is_pinned("TOKEN")

    def test_unpin_not_pinned_raises(self, mgr):
        with pytest.raises(PinError, match="not pinned"):
            mgr.unpin("MISSING")

    def test_list_pins_sorted(self, mgr):
        mgr.pin("ZEBRA")
        mgr.pin("ALPHA")
        mgr.pin("MANGO")
        assert mgr.list_pins() == ["ALPHA", "MANGO", "ZEBRA"]

    def test_assert_writable_raises_when_pinned(self, mgr):
        mgr.pin("LOCKED")
        with pytest.raises(PinError, match="pinned"):
            mgr.assert_writable("LOCKED")

    def test_assert_writable_passes_when_not_pinned(self, mgr):
        mgr.assert_writable("FREE_KEY")  # should not raise

    def test_is_pinned_false_for_unknown_key(self, mgr):
        assert not mgr.is_pinned("UNKNOWN")

    def test_unpin_removes_from_list(self, mgr):
        mgr.pin("A")
        mgr.pin("B")
        mgr.unpin("A")
        assert mgr.list_pins() == ["B"]
