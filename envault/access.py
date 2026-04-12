"""Access control for vault keys — define read/write permissions per key or pattern."""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path
from typing import Dict, List, Optional


class AccessError(Exception):
    """Raised when an access control violation or configuration error occurs."""


ACCESS_FILE = "access.json"


class AccessManager:
    """Manages per-key and glob-pattern access rules stored alongside the vault."""

    def __init__(self, vault_dir: str) -> None:
        self._path = Path(vault_dir) / ACCESS_FILE
        self._rules: Dict[str, List[str]] = self._load()

    def _load(self) -> Dict[str, List[str]]:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text())
            except json.JSONDecodeError as exc:
                raise AccessError(f"Malformed access file {self._path}: {exc}") from exc
            if not isinstance(data, dict):
                raise AccessError(f"Access file {self._path} must contain a JSON object")
            return data
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._rules, indent=2))

    def set_permissions(self, pattern: str, permissions: List[str]) -> None:
        """Set allowed operations ('read', 'write') for a key pattern."""
        valid = {"read", "write"}
        bad = set(permissions) - valid
        if bad:
            raise AccessError(f"Invalid permissions: {bad}. Allowed: {valid}")
        self._rules[pattern] = list(permissions)
        self._save()

    def remove_permissions(self, pattern: str) -> None:
        """Remove access rules for a pattern."""
        if pattern not in self._rules:
            raise AccessError(f"No rules defined for pattern: {pattern!r}")
        del self._rules[pattern]
        self._save()

    def get_permissions(self, key: str) -> List[str]:
        """Return effective permissions for a key by matching rules in insertion order."""
        for pattern, perms in self._rules.items():
            if fnmatch.fnmatch(key, pattern):
                return perms
        return ["read", "write"]  # default: full access

    def can_read(self, key: str) -> bool:
        return "read" in self.get_permissions(key)

    def can_write(self, key: str) -> bool:
        return "write" in self.get_permissions(key)

    def list_rules(self) -> Dict[str, List[str]]:
        return dict(self._rules)
