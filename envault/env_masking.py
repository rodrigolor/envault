"""Masking support for sensitive environment variable values."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class MaskingError(Exception):
    """Raised when a masking operation fails."""


class MaskingManager:
    """Manages which keys should have their values masked in output."""

    MASK_PLACEHOLDER = "********"
    _FILENAME = "masked_keys.json"

    def __init__(self, vault_dir: str | Path) -> None:
        self._path = Path(vault_dir) / self._FILENAME
        self._masked: List[str] = self._load()

    def _load(self) -> List[str]:
        if not self._path.exists():
            return []
        try:
            return json.loads(self._path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            raise MaskingError(f"Failed to load masked keys: {exc}") from exc

    def _save(self) -> None:
        try:
            self._path.write_text(json.dumps(self._masked, indent=2))
        except OSError as exc:
            raise MaskingError(f"Failed to save masked keys: {exc}") from exc

    def mask(self, key: str) -> None:
        """Mark a key as masked."""
        if key not in self._masked:
            self._masked.append(key)
            self._save()

    def unmask(self, key: str) -> None:
        """Remove masking from a key."""
        if key not in self._masked:
            raise MaskingError(f"Key '{key}' is not masked.")
        self._masked.remove(key)
        self._save()

    def is_masked(self, key: str) -> bool:
        """Return True if the key is currently masked."""
        return key in self._masked

    def list_masked(self) -> List[str]:
        """Return all currently masked keys."""
        return list(self._masked)

    def apply(self, variables: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of variables with masked values replaced."""
        return {
            k: (self.MASK_PLACEHOLDER if self.is_masked(k) else v)
            for k, v in variables.items()
        }
