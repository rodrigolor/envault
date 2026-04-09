"""Audit log for tracking vault operations."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


AUDIT_LOG_FILENAME = "audit.log"


class AuditLog:
    """Records and retrieves audit events for vault operations."""

    def __init__(self, base_dir: str, profile: str = "default"):
        self.log_path = Path(base_dir) / profile / AUDIT_LOG_FILENAME
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, action: str, key: Optional[str] = None, profile: str = "default") -> None:
        """Append an audit event to the log file."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "profile": profile,
        }
        if key is not None:
            event["key"] = key

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def read(self, limit: Optional[int] = None) -> List[dict]:
        """Return audit events, most recent last. Optionally limit results."""
        if not self.log_path.exists():
            return []

        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        events = [json.loads(line) for line in lines]
        if limit is not None:
            events = events[-limit:]
        return events

    def clear(self) -> None:
        """Remove all audit log entries."""
        if self.log_path.exists():
            os.remove(self.log_path)
