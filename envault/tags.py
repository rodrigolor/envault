"""Tag management for grouping and organizing vault variables."""

from typing import Dict, List, Optional


class TagError(Exception):
    pass


class TagManager:
    """Manages tags associated with vault environment variable keys."""

    def __init__(self, vault):
        self._vault = vault
        self._tags: Dict[str, List[str]] = {}  # key -> list of tags
        self._load()

    def _load(self):
        """Load tag metadata from vault storage if available."""
        raw = self._vault.get("__tags__")
        if raw:
            import json
            try:
                self._tags = json.loads(raw)
            except (ValueError, TypeError):
                self._tags = {}

    def _save(self):
        """Persist tag metadata into the vault."""
        import json
        self._vault.set("__tags__", json.dumps(self._tags))

    def tag(self, key: str, tag: str) -> None:
        """Add a tag to a key."""
        if not self._vault.get(key):
            raise TagError(f"Key '{key}' does not exist in vault.")
        tags = self._tags.get(key, [])
        if tag not in tags:
            tags.append(tag)
        self._tags[key] = tags
        self._save()

    def untag(self, key: str, tag: str) -> None:
        """Remove a tag from a key."""
        tags = self._tags.get(key, [])
        if tag not in tags:
            raise TagError(f"Tag '{tag}' not found on key '{key}'.")
        tags.remove(tag)
        self._tags[key] = tags
        self._save()

    def get_tags(self, key: str) -> List[str]:
        """Return all tags for a given key."""
        return list(self._tags.get(key, []))

    def find_by_tag(self, tag: str) -> List[str]:
        """Return all keys that have the given tag."""
        return [k for k, tags in self._tags.items() if tag in tags]

    def list_all_tags(self) -> List[str]:
        """Return a sorted unique list of all tags in use."""
        all_tags = set()
        for tags in self._tags.values():
            all_tags.update(tags)
        return sorted(all_tags)
