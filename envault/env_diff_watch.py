"""Live environment diff watcher — detects changes to vault variables at runtime."""

from __future__ import annotations

import time
import threading
from typing import Callable, Dict, Optional


class EnvDiffWatchError(Exception):
    pass


class EnvDiffWatcher:
    """Polls a vault for changes and fires callbacks when variables are added,
    modified, or removed."""

    def __init__(self, vault, interval: float = 5.0):
        self._vault = vault
        self._interval = interval
        self._snapshot: Dict[str, str] = {}
        self._callbacks: Dict[str, list[Callable]] = {
            "added": [],
            "modified": [],
            "removed": [],
        }
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def on(self, event: str, callback: Callable) -> None:
        """Register a callback for 'added', 'modified', or 'removed' events."""
        if event not in self._callbacks:
            raise EnvDiffWatchError(f"Unknown event: {event!r}. Use: {list(self._callbacks)}.")
        self._callbacks[event].append(callback)

    def _get_current(self) -> Dict[str, str]:
        try:
            return dict(self._vault.get_all())
        except Exception as exc:
            raise EnvDiffWatchError(f"Failed to read vault: {exc}") from exc

    def _compute_diff(self, old: Dict[str, str], new: Dict[str, str]):
        added = {k: new[k] for k in new if k not in old}
        removed = {k: old[k] for k in old if k not in new}
        modified = {k: (old[k], new[k]) for k in new if k in old and old[k] != new[k]}
        return added, modified, removed

    def _fire(self, event: str, payload):
        for cb in self._callbacks[event]:
            cb(payload)

    def _poll(self):
        self._snapshot = self._get_current()
        while not self._stop_event.is_set():
            self._stop_event.wait(self._interval)
            if self._stop_event.is_set():
                break
            current = self._get_current()
            added, modified, removed = self._compute_diff(self._snapshot, current)
            if added:
                self._fire("added", added)
            if modified:
                self._fire("modified", modified)
            if removed:
                self._fire("removed", removed)
            self._snapshot = current

    def start(self) -> None:
        """Start watching in a background thread."""
        if self._thread and self._thread.is_alive():
            raise EnvDiffWatchError("Watcher is already running.")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background watcher thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._interval + 1)
            self._thread = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
