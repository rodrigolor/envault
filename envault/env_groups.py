"""Group management for environment variables."""

import json
from pathlib import Path
from typing import Dict, List, Optional


class GroupError(Exception):
    pass


class GroupManager:
    """Manage named groups of environment variable keys."""

    def __init__(self, base_dir: str):
        self._path = Path(base_dir) / "groups.json"
        self._groups: Dict[str, List[str]] = self._load()

    def _load(self) -> Dict[str, List[str]]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._groups, indent=2))

    def create(self, group: str) -> None:
        """Create an empty group."""
        if group in self._groups:
            raise GroupError(f"Group '{group}' already exists.")
        self._groups[group] = []
        self._save()

    def delete(self, group: str) -> None:
        """Delete a group."""
        if group not in self._groups:
            raise GroupError(f"Group '{group}' does not exist.")
        del self._groups[group]
        self._save()

    def add_key(self, group: str, key: str) -> None:
        """Add a key to a group."""
        if group not in self._groups:
            raise GroupError(f"Group '{group}' does not exist.")
        if key in self._groups[group]:
            raise GroupError(f"Key '{key}' already in group '{group}'.")
        self._groups[group].append(key)
        self._save()

    def remove_key(self, group: str, key: str) -> None:
        """Remove a key from a group."""
        if group not in self._groups:
            raise GroupError(f"Group '{group}' does not exist.")
        if key not in self._groups[group]:
            raise GroupError(f"Key '{key}' not in group '{group}'.")
        self._groups[group].remove(key)
        self._save()

    def list_groups(self) -> List[str]:
        """Return all group names."""
        return list(self._groups.keys())

    def get_keys(self, group: str) -> List[str]:
        """Return all keys in a group."""
        if group not in self._groups:
            raise GroupError(f"Group '{group}' does not exist.")
        return list(self._groups[group])

    def find_groups_for_key(self, key: str) -> List[str]:
        """Return all groups that contain the given key."""
        return [g for g, keys in self._groups.items() if key in keys]
