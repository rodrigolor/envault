from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class CategoryError(Exception):
    pass


class CategoryManager:
    """Manage logical categories for environment variable keys."""

    _FILENAME = "categories.json"

    def __init__(self, vault_dir: str) -> None:
        self._path = Path(vault_dir) / self._FILENAME
        self._data: Dict[str, str] = self._load()

    def _load(self) -> Dict[str, str]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def assign(self, key: str, category: str) -> None:
        """Assign *key* to *category*."""
        if not key:
            raise CategoryError("Key must not be empty.")
        if not category:
            raise CategoryError("Category must not be empty.")
        self._data[key] = category
        self._save()

    def unassign(self, key: str) -> None:
        """Remove category assignment for *key*."""
        if key not in self._data:
            raise CategoryError(f"Key '{key}' has no category assigned.")
        del self._data[key]
        self._save()

    def get_category(self, key: str) -> Optional[str]:
        """Return the category for *key*, or None if unassigned."""
        return self._data.get(key)

    def list_by_category(self, category: str) -> List[str]:
        """Return all keys belonging to *category*."""
        return [k for k, v in self._data.items() if v == category]

    def list_all(self) -> Dict[str, str]:
        """Return a mapping of key -> category for all assigned keys."""
        return dict(self._data)

    def list_categories(self) -> List[str]:
        """Return sorted list of distinct category names in use."""
        return sorted(set(self._data.values()))
