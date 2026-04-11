"""Vault watchdog: monitors vault keys for changes and triggers callbacks."""

from __future__ import annotations

import time
import threading
from typing import Callable, Dict, Optional


class WatchdogError(Exception):
    """Raised when the watchdog encounters an error."""


class VaultWatchdog:
    """Polls the vault at a configurable interval and fires callbacks on changes."""

    def __init__(self, vault, interval: float = 5.0) -> None:
        self._vault = vault
        self._interval = interval
        self._callbacks: Dict[str, list[Callable[[str, Optional[str], Optional[str]], None]]] = {}
        self._snapshot: Dict[str, str] = {}
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running = False

    def watch(self, key: str, callback: Callable[[str, Optional[str], Optional[str]], None]) -> None:
        """Register a callback for changes to *key*.

        The callback receives (key, old_value, new_value).
        new_value is None when the key is deleted.
        """
        self._callbacks.setdefault(key, []).append(callback)

    def unwatch(self, key: str) -> None:
        """Remove all callbacks for *key*."""
        self._callbacks.pop(key, None)

    def start(self) -> None:
        """Start the background polling thread."""
        if self._running:
            raise WatchdogError("Watchdog is already running.")
        self._snapshot = dict(self._vault.get_all())
        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background polling thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._interval + 1)
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def _poll_loop(self) -> None:
        while not self._stop_event.wait(timeout=self._interval):
            self._check()

    def _check(self) -> None:
        try:
            current = dict(self._vault.get_all())
        except Exception as exc:  # noqa: BLE001
            raise WatchdogError(f"Failed to read vault: {exc}") from exc

        watched_keys = set(self._callbacks)
        for key in watched_keys:
            old = self._snapshot.get(key)
            new = current.get(key)
            if old != new:
                for cb in self._callbacks.get(key, []):
                    cb(key, old, new)

        self._snapshot = current
