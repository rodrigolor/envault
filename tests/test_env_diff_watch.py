"""Tests for EnvDiffWatcher."""

import pytest
from envault.env_diff_watch import EnvDiffWatcher, EnvDiffWatchError


class FakeVault:
    def __init__(self, data: dict):
        self._data = dict(data)

    def get_all(self):
        return dict(self._data)

    def set(self, key, value):
        self._data[key] = value

    def delete(self, key):
        self._data.pop(key, None)


@pytest.fixture
def vault():
    return FakeVault({"FOO": "bar", "BAZ": "qux"})


@pytest.fixture
def watcher(vault):
    return EnvDiffWatcher(vault, interval=0.1)


class TestEnvDiffWatcher:
    def test_on_unknown_event_raises(self, watcher):
        with pytest.raises(EnvDiffWatchError, match="Unknown event"):
            watcher.on("explode", lambda x: x)

    def test_compute_diff_added(self, vault, watcher):
        old = {"A": "1"}
        new = {"A": "1", "B": "2"}
        added, modified, removed = watcher._compute_diff(old, new)
        assert added == {"B": "2"}
        assert modified == {}
        assert removed == {}

    def test_compute_diff_removed(self, vault, watcher):
        old = {"A": "1", "B": "2"}
        new = {"A": "1"}
        added, modified, removed = watcher._compute_diff(old, new)
        assert added == {}
        assert removed == {"B": "2"}

    def test_compute_diff_modified(self, vault, watcher):
        old = {"A": "1"}
        new = {"A": "99"}
        added, modified, removed = watcher._compute_diff(old, new)
        assert modified == {"A": ("1", "99")}

    def test_compute_diff_no_changes(self, watcher):
        state = {"X": "y"}
        added, modified, removed = watcher._compute_diff(state, state)
        assert not added and not modified and not removed

    def test_start_and_stop(self, watcher):
        watcher.start()
        assert watcher.is_running
        watcher.stop()
        assert not watcher.is_running

    def test_double_start_raises(self, watcher):
        watcher.start()
        try:
            with pytest.raises(EnvDiffWatchError, match="already running"):
                watcher.start()
        finally:
            watcher.stop()

    def test_callback_fires_on_added(self, vault):
        watcher = EnvDiffWatcher(vault, interval=0.05)
        events = []
        watcher.on("added", lambda p: events.append(("added", p)))
        watcher._snapshot = dict(vault.get_all())
        vault.set("NEW_KEY", "hello")
        current = watcher._get_current()
        added, modified, removed = watcher._compute_diff(watcher._snapshot, current)
        if added:
            watcher._fire("added", added)
        assert any(e[0] == "added" and "NEW_KEY" in e[1] for e in events)

    def test_callback_fires_on_removed(self, vault):
        watcher = EnvDiffWatcher(vault, interval=0.05)
        events = []
        watcher.on("removed", lambda p: events.append(("removed", p)))
        watcher._snapshot = dict(vault.get_all())
        vault.delete("FOO")
        current = watcher._get_current()
        _, _, removed = watcher._compute_diff(watcher._snapshot, current)
        if removed:
            watcher._fire("removed", removed)
        assert any(e[0] == "removed" and "FOO" in e[1] for e in events)
