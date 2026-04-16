"""Human-readable descriptions for environment variable keys."""

import json
from pathlib import Path


class DescriptionError(Exception):
    pass


class DescriptionManager:
    FILE = "descriptions.json"

    def __init__(self, vault_dir: str):
        self._path = Path(vault_dir) / self.FILE
        self._data: dict = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self):
        self._path.write_text(json.dumps(self._data, indent=2))

    def set(self, key: str, description: str):
        if not key:
            raise DescriptionError("Key must not be empty.")
        self._data[key] = description
        self._save()

    def get(self, key: str) -> str | None:
        return self._data.get(key)

    def remove(self, key: str):
        if key not in self._data:
            raise DescriptionError(f"No description found for key: {key}")
        del self._data[key]
        self._save()

    def list_all(self) -> dict:
        return dict(self._data)

    def annotate(self, vault_keys: list[str]) -> dict:
        """Return descriptions only for keys that exist in the vault."""
        return {k: self._data.get(k, "") for k in vault_keys}
