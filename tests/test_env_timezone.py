"""Tests for envault.env_timezone."""

from __future__ import annotations

import pytest

from envault.env_timezone import TimezoneError, TimezoneManager


@pytest.fixture()
def mgr(tmp_path):
    return TimezoneManager(tmp_path)


class TestTimezoneManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_all() == {}

    def test_set_and_get_timezone(self, mgr):
        mgr.set_timezone("CREATED_AT", "UTC")
        assert mgr.get_timezone("CREATED_AT") == "UTC"

    def test_set_persists_to_disk(self, tmp_path):
        mgr1 = TimezoneManager(tmp_path)
        mgr1.set_timezone("LOG_TIME", "America/New_York")
        mgr2 = TimezoneManager(tmp_path)
        assert mgr2.get_timezone("LOG_TIME") == "America/New_York"

    def test_get_unknown_key_returns_none(self, mgr):
        assert mgr.get_timezone("NONEXISTENT") is None

    def test_invalid_timezone_raises(self, mgr):
        with pytest.raises(TimezoneError, match="Unknown timezone"):
            mgr.set_timezone("KEY", "Mars/OlympusMons")

    def test_remove_timezone(self, mgr):
        mgr.set_timezone("TS", "Europe/London")
        mgr.remove_timezone("TS")
        assert mgr.get_timezone("TS") is None

    def test_remove_nonexistent_raises(self, mgr):
        with pytest.raises(TimezoneError, match="No timezone set"):
            mgr.remove_timezone("GHOST")

    def test_list_all_returns_copy(self, mgr):
        mgr.set_timezone("A", "UTC")
        mgr.set_timezone("B", "Asia/Tokyo")
        result = mgr.list_all()
        assert result == {"A": "UTC", "B": "Asia/Tokyo"}
        result["C"] = "junk"
        assert "C" not in mgr.list_all()

    def test_keys_in_timezone(self, mgr):
        mgr.set_timezone("A", "UTC")
        mgr.set_timezone("B", "UTC")
        mgr.set_timezone("C", "Asia/Tokyo")
        assert sorted(mgr.keys_in_timezone("UTC")) == ["A", "B"]
        assert mgr.keys_in_timezone("Asia/Tokyo") == ["C"]

    def test_keys_in_timezone_empty_when_none_match(self, mgr):
        mgr.set_timezone("A", "UTC")
        assert mgr.keys_in_timezone("Europe/Paris") == []

    def test_overwrite_timezone(self, mgr):
        mgr.set_timezone("TS", "UTC")
        mgr.set_timezone("TS", "Pacific/Auckland")
        assert mgr.get_timezone("TS") == "Pacific/Auckland"
        assert len(mgr.list_all()) == 1
