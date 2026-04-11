"""Tests for envault.watchdog."""

from __future__ import annotations

import threading
import time
import pytest

from envault.watchdog import VaultWatchdog, WatchdogError


class FakeVault:
    def __init__(self, data: dict | None = None) -> None:
        self._data: dict = data or {}

    def get_all(self) -> dict:
        return dict(self._data)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)


@pytest.fixture()
def vault():
    return FakeVault({"KEY1": "alpha", "KEY2": "beta"})


@pytest.fixture()
def watchdog(vault):
    wd = VaultWatchdog(vault, interval=0.05)
    yield wd
    if wd.is_running:
        wd.stop()


class TestVaultWatchdog:
    def test_initial_state_not_running(self, watchdog):
        assert not watchdog.is_running

    def test_start_sets_running(self, watchdog):
        watchdog.start()
        assert watchdog.is_running

    def test_stop_clears_running(self, watchdog):
        watchdog.start()
        watchdog.stop()
        assert not watchdog.is_running

    def test_double_start_raises(self, watchdog):
        watchdog.start()
        with pytest.raises(WatchdogError, match="already running"):
            watchdog.start()

    def test_callback_fired_on_value_change(self, vault, watchdog):
        events = []
        watchdog.watch("KEY1", lambda k, o, n: events.append((k, o, n)))
        watchdog.start()
        vault.set("KEY1", "changed")
        time.sleep(0.3)
        watchdog.stop()
        assert len(events) == 1
        assert events[0] == ("KEY1", "alpha", "changed")

    def test_callback_fired_on_key_deletion(self, vault, watchdog):
        events = []
        watchdog.watch("KEY2", lambda k, o, n: events.append((k, o, n)))
        watchdog.start()
        vault.delete("KEY2")
        time.sleep(0.3)
        watchdog.stop()
        assert len(events) == 1
        assert events[0] == ("KEY2", "beta", None)

    def test_no_callback_when_value_unchanged(self, vault, watchdog):
        events = []
        watchdog.watch("KEY1", lambda k, o, n: events.append((k, o, n)))
        watchdog.start()
        time.sleep(0.3)
        watchdog.stop()
        assert events == []

    def test_unwatch_stops_callbacks(self, vault, watchdog):
        events = []
        watchdog.watch("KEY1", lambda k, o, n: events.append((k, o, n)))
        watchdog.unwatch("KEY1")
        watchdog.start()
        vault.set("KEY1", "changed")
        time.sleep(0.3)
        watchdog.stop()
        assert events == []

    def test_multiple_callbacks_same_key(self, vault, watchdog):
        results_a, results_b = [], []
        watchdog.watch("KEY1", lambda k, o, n: results_a.append(n))
        watchdog.watch("KEY1", lambda k, o, n: results_b.append(n))
        watchdog.start()
        vault.set("KEY1", "new")
        time.sleep(0.3)
        watchdog.stop()
        assert results_a == ["new"]
        assert results_b == ["new"]
