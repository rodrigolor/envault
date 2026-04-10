"""Tests for NotificationManager."""

from __future__ import annotations

from pathlib import Path

import pytest

from envault.notifications import NotificationError, NotificationEvent, NotificationManager


@pytest.fixture
def mgr(tmp_path: Path) -> NotificationManager:
    return NotificationManager(tmp_path / "notifications.json")


class TestNotificationManager:
    def test_supported_events_are_known(self, mgr: NotificationManager) -> None:
        assert "ttl_expired" in mgr.SUPPORTED_EVENTS
        assert "key_rotated" in mgr.SUPPORTED_EVENTS

    def test_register_and_dispatch_handler(self, mgr: NotificationManager) -> None:
        received: list[NotificationEvent] = []
        mgr.register_handler("ttl_expired", received.append)
        event = NotificationEvent("ttl_expired", "MY_KEY", "Key has expired.")
        mgr.notify(event)
        assert len(received) == 1
        assert received[0].key == "MY_KEY"

    def test_multiple_handlers_all_called(self, mgr: NotificationManager) -> None:
        calls: list[str] = []
        mgr.register_handler("key_rotated", lambda e: calls.append("h1"))
        mgr.register_handler("key_rotated", lambda e: calls.append("h2"))
        mgr.notify(NotificationEvent("key_rotated", "K", "rotated"))
        assert calls == ["h1", "h2"]

    def test_register_unknown_event_raises(self, mgr: NotificationManager) -> None:
        with pytest.raises(NotificationError, match="Unknown event type"):
            mgr.register_handler("nonexistent_event", lambda e: None)

    def test_notify_unknown_event_raises(self, mgr: NotificationManager) -> None:
        with pytest.raises(NotificationError, match="Unknown event type"):
            mgr.notify(NotificationEvent("bad_event", "K", "msg"))

    def test_configure_webhook_persists(self, mgr: NotificationManager, tmp_path: Path) -> None:
        mgr.configure_webhook("access_denied", "https://example.com/hook")
        mgr2 = NotificationManager(tmp_path / "notifications.json")
        assert mgr2.get_webhooks().get("access_denied") == "https://example.com/hook"

    def test_configure_unknown_webhook_raises(self, mgr: NotificationManager) -> None:
        with pytest.raises(NotificationError, match="Unknown event type"):
            mgr.configure_webhook("unknown_event", "https://example.com")

    def test_get_webhooks_empty_initially(self, mgr: NotificationManager) -> None:
        assert mgr.get_webhooks() == {}

    def test_clear_webhook_removes_entry(self, mgr: NotificationManager) -> None:
        mgr.configure_webhook("snapshot_restored", "https://example.com/snap")
        mgr.clear_webhook("snapshot_restored")
        assert "snapshot_restored" not in mgr.get_webhooks()

    def test_clear_nonexistent_webhook_is_noop(self, mgr: NotificationManager) -> None:
        mgr.clear_webhook("ttl_expired")  # should not raise
        assert mgr.get_webhooks() == {}
