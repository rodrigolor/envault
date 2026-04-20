"""Ownership tracking for environment variable keys."""

import json
from pathlib import Path
from datetime import datetime, timezone


class OwnershipError(Exception):
    pass


class OwnershipManager:
    def __init__(self, base_dir: str):
        self._path = Path(base_dir) / "ownership.json"
        self._data: dict = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))

    def assign(self, key: str, owner: str) -> None:
        """Assign an owner to a key."""
        if not key:
            raise OwnershipError("Key must not be empty.")
        if not owner:
            raise OwnershipError("Owner must not be empty.")
        self._data[key] = {
            "owner": owner,
            "assigned_at": datetime.now(timezone.utc).isoformat(),
        }
        self._save()

    def unassign(self, key: str) -> None:
        """Remove ownership record for a key."""
        if key not in self._data:
            raise OwnershipError(f"No ownership record for key '{key}'.")
        del self._data[key]
        self._save()

    def get_owner(self, key: str) -> str | None:
        """Return the owner of a key, or None if unowned."""
        record = self._data.get(key)
        return record["owner"] if record else None

    def list_owned(self) -> dict[str, str]:
        """Return a mapping of key -> owner for all owned keys."""
        return {k: v["owner"] for k, v in self._data.items()}

    def owned_by(self, owner: str) -> list[str]:
        """Return all keys owned by the given owner."""
        return [k for k, v in self._data.items() if v["owner"] == owner]

    def transfer(self, key: str, new_owner: str) -> None:
        """Transfer ownership of a key to a new owner."""
        if key not in self._data:
            raise OwnershipError(f"No ownership record for key '{key}'.")
        if not new_owner:
            raise OwnershipError("New owner must not be empty.")
        self._data[key]["owner"] = new_owner
        self._data[key]["assigned_at"] = datetime.now(timezone.utc).isoformat()
        self._save()
