"""Tests for envault.env_expiry."""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from envault.env_expiry import ExpiryError, ExpiryManager


@pytest.fixture
def mgr(tmp_path: Path) -> ExpiryManager:
    return ExpiryManager(tmp_path)


class TestExpiryManager:
    def test_list_empty_initially(self, mgr: ExpiryManager) -> None:
        assert mgr.list_expiring() == {}

    def test_set_and_get_expiry(self, mgr: ExpiryManager) -> None:
        future = datetime(2099, 1, 1, tzinfo=timezone.utc)
        mgr.set_expiry("MY_KEY", future)
        result = mgr.get_expiry("MY_KEY")
        assert result is not None
        assert result.year == 2099

    def test_set_expiry_persists_to_disk(self, mgr: ExpiryManager, tmp_path: Path) -> None:
        future = datetime(2099, 6, 15, tzinfo=timezone.utc)
        mgr.set_expiry("PERSIST_KEY", future)
        mgr2 = ExpiryManager(tmp_path)
        assert mgr2.get_expiry("PERSIST_KEY") is not None

    def test_get_expiry_returns_none_for_unknown_key(self, mgr: ExpiryManager) -> None:
        assert mgr.get_expiry("UNKNOWN") is None

    def test_is_expired_false_for_future(self, mgr: ExpiryManager) -> None:
        future = datetime.now(tz=timezone.utc) + timedelta(days=365)
        mgr.set_expiry("FUTURE_KEY", future)
        assert mgr.is_expired("FUTURE_KEY") is False

    def test_is_expired_true_for_past(self, mgr: ExpiryManager) -> None:
        past = datetime.now(tz=timezone.utc) - timedelta(seconds=1)
        mgr.set_expiry("PAST_KEY", past)
        assert mgr.is_expired("PAST_KEY") is True

    def test_is_expired_false_when_no_expiry(self, mgr: ExpiryManager) -> None:
        assert mgr.is_expired("NO_EXPIRY") is False

    def test_remove_expiry(self, mgr: ExpiryManager) -> None:
        future = datetime.now(tz=timezone.utc) + timedelta(days=10)
        mgr.set_expiry("REM_KEY", future)
        mgr.remove_expiry("REM_KEY")
        assert mgr.get_expiry("REM_KEY") is None

    def test_remove_expiry_raises_if_not_set(self, mgr: ExpiryManager) -> None:
        with pytest.raises(ExpiryError, match="No expiry set"):
            mgr.remove_expiry("GHOST")

    def test_list_expired_returns_only_past_keys(self, mgr: ExpiryManager) -> None:
        past = datetime.now(tz=timezone.utc) - timedelta(seconds=5)
        future = datetime.now(tz=timezone.utc) + timedelta(days=1)
        mgr.set_expiry("OLD", past)
        mgr.set_expiry("NEW", future)
        expired = mgr.list_expired()
        assert "OLD" in expired
        assert "NEW" not in expired

    def test_naive_datetime_treated_as_utc(self, mgr: ExpiryManager) -> None:
        naive = datetime(2099, 12, 31)  # no tzinfo
        mgr.set_expiry("NAIVE", naive)
        result = mgr.get_expiry("NAIVE")
        assert result is not None
        assert result.tzinfo is not None
