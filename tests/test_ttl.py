"""Tests for envault.ttl.TTLManager."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envault.ttl import TTLError, TTLManager


@pytest.fixture()
def mgr(tmp_path: Path) -> TTLManager:
    return TTLManager(tmp_path)


class TestTTLManager:
    def test_no_ttl_is_not_expired(self, mgr: TTLManager) -> None:
        assert mgr.is_expired("MY_KEY") is False

    def test_no_ttl_time_remaining_is_none(self, mgr: TTLManager) -> None:
        assert mgr.time_remaining("MY_KEY") is None

    def test_set_ttl_creates_json_file(self, mgr: TTLManager, tmp_path: Path) -> None:
        mgr.set_ttl("MY_KEY", 60)
        assert (tmp_path / ".ttl.json").exists()

    def test_fresh_ttl_is_not_expired(self, mgr: TTLManager) -> None:
        mgr.set_ttl("MY_KEY", 60)
        assert mgr.is_expired("MY_KEY") is False

    def test_expired_ttl_is_detected(self, mgr: TTLManager) -> None:
        mgr.set_ttl("MY_KEY", 0.01)
        time.sleep(0.05)
        assert mgr.is_expired("MY_KEY") is True

    def test_time_remaining_decreases(self, mgr: TTLManager) -> None:
        mgr.set_ttl("MY_KEY", 10)
        remaining = mgr.time_remaining("MY_KEY")
        assert remaining is not None
        assert 0 < remaining <= 10

    def test_clear_ttl_removes_entry(self, mgr: TTLManager) -> None:
        mgr.set_ttl("MY_KEY", 60)
        mgr.clear_ttl("MY_KEY")
        assert mgr.time_remaining("MY_KEY") is None
        assert mgr.is_expired("MY_KEY") is False

    def test_purge_expired_returns_expired_keys(self, mgr: TTLManager) -> None:
        mgr.set_ttl("GONE", 0.01)
        mgr.set_ttl("ALIVE", 60)
        time.sleep(0.05)
        expired = mgr.purge_expired()
        assert "GONE" in expired
        assert "ALIVE" not in expired

    def test_purge_expired_removes_from_all_ttls(self, mgr: TTLManager) -> None:
        mgr.set_ttl("GONE", 0.01)
        time.sleep(0.05)
        mgr.purge_expired()
        assert "GONE" not in mgr.all_ttls()

    def test_all_ttls_excludes_expired(self, mgr: TTLManager) -> None:
        mgr.set_ttl("GONE", 0.01)
        mgr.set_ttl("ALIVE", 60)
        time.sleep(0.05)
        live = mgr.all_ttls()
        assert "GONE" not in live
        assert "ALIVE" in live

    def test_zero_or_negative_ttl_raises(self, mgr: TTLManager) -> None:
        with pytest.raises(TTLError):
            mgr.set_ttl("MY_KEY", 0)
        with pytest.raises(TTLError):
            mgr.set_ttl("MY_KEY", -5)

    def test_persists_across_instances(self, tmp_path: Path) -> None:
        mgr1 = TTLManager(tmp_path)
        mgr1.set_ttl("PERSIST", 60)
        mgr2 = TTLManager(tmp_path)
        assert mgr2.time_remaining("PERSIST") is not None
