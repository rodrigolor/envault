"""Pre/post hooks for vault operations."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List, Optional


class HookError(Exception):
    """Raised when a hook fails to execute."""


HOOK_EVENTS = ("pre-set", "post-set", "pre-get", "post-get", "pre-delete", "post-delete")


class HookManager:
    """Manages shell hooks that run before/after vault operations."""

    def __init__(self, vault_dir: Path) -> None:
        self._path = Path(vault_dir) / "hooks.json"
        self._hooks: dict = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {event: [] for event in HOOK_EVENTS}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._hooks, indent=2))

    def register(self, event: str, command: str) -> None:
        """Register a shell command for a given hook event."""
        if event not in HOOK_EVENTS:
            raise HookError(f"Unknown hook event '{event}'. Valid events: {HOOK_EVENTS}")
        if event not in self._hooks:
            self._hooks[event] = []
        if command not in self._hooks[event]:
            self._hooks[event].append(command)
        self._save()

    def unregister(self, event: str, command: str) -> None:
        """Remove a registered hook command."""
        if event not in self._hooks or command not in self._hooks.get(event, []):
            raise HookError(f"Hook '{command}' not found for event '{event}'")
        self._hooks[event].remove(command)
        self._save()

    def list_hooks(self, event: Optional[str] = None) -> dict:
        """Return all hooks, optionally filtered by event."""
        if event:
            if event not in HOOK_EVENTS:
                raise HookError(f"Unknown hook event '{event}'")
            return {event: self._hooks.get(event, [])}
        return dict(self._hooks)

    def run(self, event: str, env: Optional[dict] = None) -> List[str]:
        """Execute all hooks for the given event. Returns list of outputs."""
        if event not in HOOK_EVENTS:
            raise HookError(f"Unknown hook event '{event}'")
        outputs = []
        for cmd in self._hooks.get(event, []):
            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, timeout=10,
                    env=env
                )
                if result.returncode != 0:
                    raise HookError(
                        f"Hook '{cmd}' for event '{event}' failed: {result.stderr.strip()}"
                    )
                outputs.append(result.stdout.strip())
            except subprocess.TimeoutExpired:
                raise HookError(f"Hook '{cmd}' timed out after 10 seconds")
        return outputs
