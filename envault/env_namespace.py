"""Namespace management for environment variables."""

import json
from pathlib import Path


class NamespaceError(Exception):
    pass


class NamespaceManager:
    """Groups environment variable keys under named namespaces."""

    def __init__(self, base_dir: str):
        self._path = Path(base_dir) / "namespaces.json"
        self._data: dict[str, list[str]] = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2))

    def create(self, namespace: str):
        if namespace in self._data:
            raise NamespaceError(f"Namespace '{namespace}' already exists.")
        self._data[namespace] = []
        self._save()

    def delete(self, namespace: str):
        if namespace not in self._data:
            raise NamespaceError(f"Namespace '{namespace}' does not exist.")
        del self._data[namespace]
        self._save()

    def assign(self, namespace: str, key: str):
        if namespace not in self._data:
            raise NamespaceError(f"Namespace '{namespace}' does not exist.")
        if key not in self._data[namespace]:
            self._data[namespace].append(key)
            self._save()

    def unassign(self, namespace: str, key: str):
        if namespace not in self._data:
            raise NamespaceError(f"Namespace '{namespace}' does not exist.")
        if key not in self._data[namespace]:
            raise NamespaceError(f"Key '{key}' is not in namespace '{namespace}'.")
        self._data[namespace].remove(key)
        self._save()

    def list_namespaces(self) -> list[str]:
        return list(self._data.keys())

    def keys_in(self, namespace: str) -> list[str]:
        if namespace not in self._data:
            raise NamespaceError(f"Namespace '{namespace}' does not exist.")
        return list(self._data[namespace])

    def namespace_of(self, key: str) -> str | None:
        for ns, keys in self._data.items():
            if key in keys:
                return ns
        return None
