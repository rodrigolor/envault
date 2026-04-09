"""Template management for envault — allows defining and applying variable templates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional


class TemplateError(Exception):
    """Raised when a template operation fails."""


class TemplateManager:
    """Manages named templates of environment variable sets."""

    def __init__(self, base_dir: str | Path) -> None:
        self._path = Path(base_dir) / "templates.json"
        self._data: Dict[str, Dict[str, str]] = self._load()

    def _load(self) -> Dict[str, Dict[str, str]]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))

    def save_template(self, name: str, variables: Dict[str, str]) -> None:
        """Save a named template with the given variables."""
        if not name:
            raise TemplateError("Template name must not be empty.")
        self._data[name] = dict(variables)
        self._save()

    def load_template(self, name: str) -> Dict[str, str]:
        """Return variables stored under *name*."""
        if name not in self._data:
            raise TemplateError(f"Template '{name}' does not exist.")
        return dict(self._data[name])

    def delete_template(self, name: str) -> None:
        """Remove a template by name."""
        if name not in self._data:
            raise TemplateError(f"Template '{name}' does not exist.")
        del self._data[name]
        self._save()

    def list_templates(self) -> List[str]:
        """Return a sorted list of all template names."""
        return sorted(self._data.keys())

    def apply_template(self, name: str, vault) -> int:
        """Write all variables from template *name* into *vault*. Returns count."""
        variables = self.load_template(name)
        for key, value in variables.items():
            vault.set(key, value)
        return len(variables)
