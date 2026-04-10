"""Notification hooks for vault events (e.g. expiry, rotation, access)."""

from __future__ import annotations

import json
import smtplib
import subprocess
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path
from typing import Callable, Dict, List, Optional


class NotificationError(Exception):
    """Raised when a notification cannot be delivered."""


@dataclass
class NotificationEvent:
    event_type: str  # e.g. "ttl_expired", "key_rotated", "access_denied"
    key: str
    message: str
    metadata: Dict = field(default_factory=dict)


class NotificationManager:
    """Manages and dispatches vault event notifications."""

    SUPPORTED_EVENTS = {"ttl_expired", "key_rotated", "access_denied", "snapshot_restored"}

    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._handlers: Dict[str, List[Callable[[NotificationEvent], None]]] = {
            e: [] for e in self.SUPPORTED_EVENTS
        }
        self._config = self._load()

    def _load(self) -> dict:
        if self._config_path.exists():
            return json.loads(self._config_path.read_text())
        return {}

    def _save(self) -> None:
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config_path.write_text(json.dumps(self._config, indent=2))

    def register_handler(self, event_type: str, handler: Callable[[NotificationEvent], None]) -> None:
        if event_type not in self.SUPPORTED_EVENTS:
            raise NotificationError(f"Unknown event type: {event_type!r}")
        self._handlers[event_type].append(handler)

    def configure_webhook(self, event_type: str, url: str) -> None:
        if event_type not in self.SUPPORTED_EVENTS:
            raise NotificationError(f"Unknown event type: {event_type!r}")
        self._config.setdefault("webhooks", {})[event_type] = url
        self._save()

    def notify(self, event: NotificationEvent) -> None:
        if event.event_type not in self.SUPPORTED_EVENTS:
            raise NotificationError(f"Unknown event type: {event.event_type!r}")
        for handler in self._handlers.get(event.event_type, []):
            handler(event)

    def get_webhooks(self) -> Dict[str, str]:
        return dict(self._config.get("webhooks", {}))

    def clear_webhook(self, event_type: str) -> None:
        webhooks = self._config.get("webhooks", {})
        webhooks.pop(event_type, None)
        self._save()
