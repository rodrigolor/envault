"""Search and filter environment variables within a vault."""

from __future__ import annotations

import fnmatch
import re
from typing import Dict, List, Optional


class SearchError(Exception):
    """Raised when a search operation fails."""


class SearchManager:
    """Provides search and filter capabilities over vault variables."""

    def __init__(self, vault) -> None:
        self.vault = vault

    def search(self, pattern: str, mode: str = "glob") -> Dict[str, str]:
        """Search variables by key pattern.

        Args:
            pattern: The pattern to match against variable keys.
            mode: Matching mode — 'glob', 'regex', or 'prefix'.

        Returns:
            A dict of matching key/value pairs.

        Raises:
            SearchError: If mode is invalid or regex is malformed.
        """
        all_vars = self.vault.get_all()

        if mode == "glob":
            return {k: v for k, v in all_vars.items() if fnmatch.fnmatch(k, pattern)}
        elif mode == "prefix":
            return {k: v for k, v in all_vars.items() if k.startswith(pattern)}
        elif mode == "regex":
            try:
                compiled = re.compile(pattern)
            except re.error as exc:
                raise SearchError(f"Invalid regex pattern: {exc}") from exc
            return {k: v for k, v in all_vars.items() if compiled.search(k)}
        else:
            raise SearchError(f"Unknown search mode: '{mode}'. Use 'glob', 'prefix', or 'regex'.")

    def filter_by_value(self, substring: str) -> Dict[str, str]:
        """Return variables whose values contain the given substring."""
        all_vars = self.vault.get_all()
        return {k: v for k, v in all_vars.items() if substring in v}

    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """List all variable keys, optionally filtered by prefix."""
        all_vars = self.vault.get_all()
        keys = sorted(all_vars.keys())
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        return keys
