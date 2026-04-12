"""Profile management for envault — allows grouping env vars by named profiles (e.g. dev, prod)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

DEFAULT_PROFILE = "default"
_PROFILES_FILE = ".envault_profiles.json"


class ProfileManager:
    """Manages named profiles stored in a local JSON index file."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self._index_path = self.base_dir / _PROFILES_FILE
        self._profiles: List[str] = self._load()

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load(self) -> List[str]:
        if self._index_path.exists():
            data = json.loads(self._index_path.read_text())
            return data.get("profiles", [DEFAULT_PROFILE])
        return [DEFAULT_PROFILE]

    def _save(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._index_path.write_text(json.dumps({"profiles": self._profiles}, indent=2))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def list_profiles(self) -> List[str]:
        """Return all known profile names."""
        return list(self._profiles)

    def create_profile(self, name: str) -> None:
        """Register a new profile name."""
        if name in self._profiles:
            raise ValueError(f"Profile '{name}' already exists.")
        self._profiles.append(name)
        self._save()

    def delete_profile(self, name: str) -> None:
        """Remove a profile from the index (does NOT delete its vault file)."""
        if name == DEFAULT_PROFILE:
            raise ValueError("Cannot delete the default profile.")
        if name not in self._profiles:
            raise KeyError(f"Profile '{name}' not found.")
        self._profiles.remove(name)
        self._save()

    def rename_profile(self, old_name: str, new_name: str) -> None:
        """Rename an existing profile.

        Renames the profile in the index and moves its vault file if one exists.
        Raises ValueError if ``old_name`` does not exist, ``new_name`` is already
        taken, or an attempt is made to rename the default profile.
        """
        if old_name == DEFAULT_PROFILE:
            raise ValueError("Cannot rename the default profile.")
        if old_name not in self._profiles:
            raise KeyError(f"Profile '{old_name}' not found.")
        if new_name in self._profiles:
            raise ValueError(f"Profile '{new_name}' already exists.")

        self._profiles[self._profiles.index(old_name)] = new_name
        self._save()

        old_vault = self.vault_path(old_name)
        if old_vault.exists():
            old_vault.rename(self.vault_path(new_name))

    def exists(self, name: str) -> bool:
        return name in self._profiles

    def vault_path(self, name: str) -> Path:
        """Return the vault file path for a given profile."""
        return self.base_dir / f"{name}.vault"
