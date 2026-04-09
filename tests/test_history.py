"""Tests for envault.history module."""

from __future__ import annotations

import time

import pytest

from envault.history import HistoryManager


@pytest.fixture()
def mgr(tmp_path):
    return HistoryManager(base_dir=tmp_path)


class TestHistoryManager:
    def test_get_history_empty_when_no_events(self, mgr):
        assert mgr.get_history("MY_KEY") == []

    def test_record_creates_history_file(self, mgr):
        mgr.record("DB_URL", action="set")
        assert mgr.history_file.exists()

    def test_record_and_retrieve_single_event(self, mgr):
        before = time.time()
        mgr.record("API_KEY", action="set", actor="user")
        after = time.time()

        events = mgr.get_history("API_KEY")
        assert len(events) == 1
        evt = events[0]
        assert evt["action"] == "set"
        assert evt["actor"] == "user"
        assert before <= evt["timestamp"] <= after

    def test_multiple_events_are_ordered_oldest_first(self, mgr):
        mgr.record("TOKEN", action="set")
        mgr.record("TOKEN", action="rotate")
        mgr.record("TOKEN", action="delete")

        events = mgr.get_history("TOKEN")
        assert len(events) == 3
        actions = [e["action"] for e in events]
        assert actions == ["set", "rotate", "delete"]

    def test_list_keys_returns_tracked_keys(self, mgr):
        mgr.record("KEY_A", action="set")
        mgr.record("KEY_B", action="set")

        keys = mgr.list_keys()
        assert set(keys) == {"KEY_A", "KEY_B"}

    def test_clear_specific_key(self, mgr):
        mgr.record("KEY_A", action="set")
        mgr.record("KEY_B", action="set")
        mgr.clear("KEY_A")

        assert mgr.get_history("KEY_A") == []
        assert len(mgr.get_history("KEY_B")) == 1

    def test_clear_all_history(self, mgr):
        mgr.record("KEY_A", action="set")
        mgr.record("KEY_B", action="set")
        mgr.clear()

        assert mgr.list_keys() == []

    def test_default_actor_is_cli(self, mgr):
        mgr.record("SECRET", action="set")
        evt = mgr.get_history("SECRET")[0]
        assert evt["actor"] == "cli"
