"""Placeholder resolution for environment variable values.

Allows values like '${OTHER_KEY}' to be resolved from the vault.
"""

import re
from typing import Dict, Optional


class PlaceholderError(Exception):
    pass


REF_PATTERN = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


class PlaceholderResolver:
    """Resolves ${KEY} references within environment variable values."""

    def __init__(self, vault) -> None:
        self._vault = vault

    def resolve(self, value: str, max_depth: int = 10) -> str:
        """Recursively resolve all ${KEY} placeholders in value."""
        seen: set = set()
        return self._resolve(value, seen, max_depth)

    def _resolve(self, value: str, seen: set, depth: int) -> str:
        if depth <= 0:
            raise PlaceholderError("Max recursion depth exceeded during placeholder resolution")

        def replacer(match: re.Match) -> str:
            key = match.group(1)
            if key in seen:
                raise PlaceholderError(f"Circular reference detected for key: '{key}'")
            raw = self._vault.get(key)
            if raw is None:
                raise PlaceholderError(f"Referenced key not found: '{key}'")
            seen.add(key)
            resolved = self._resolve(raw, seen, depth - 1)
            seen.discard(key)
            return resolved

        return REF_PATTERN.sub(replacer, value)

    def resolve_all(self, data: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Resolve placeholders for all keys in the vault (or provided dict)."""
        if data is None:
            data = self._vault.get_all()
        return {k: self.resolve(v) for k, v in data.items()}

    def has_placeholders(self, value: str) -> bool:
        """Return True if value contains any ${KEY} references."""
        return bool(REF_PATTERN.search(value))

    def list_references(self, value: str) -> list:
        """Return all referenced keys found in value."""
        return REF_PATTERN.findall(value)
