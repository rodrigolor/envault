"""Sorting and ordering utilities for environment variables."""

from __future__ import annotations

from typing import Dict, List, Optional


class SortError(Exception):
    """Raised when a sort operation fails."""


class EnvSorter:
    """Sorts and reorders environment variable keys."""

    SORT_MODES = ("alpha", "alpha_desc", "length", "length_desc")

    def __init__(self, vault) -> None:
        self._vault = vault

    def sort(self, mode: str = "alpha") -> Dict[str, str]:
        """Return a dict of all variables sorted by the given mode.

        Args:
            mode: One of 'alpha', 'alpha_desc', 'length', 'length_desc'.

        Returns:
            An ordered dict with keys sorted accordingly.

        Raises:
            SortError: If the mode is not recognised.
        """
        if mode not in self.SORT_MODES:
            raise SortError(
                f"Unknown sort mode '{mode}'. Choose from: {', '.join(self.SORT_MODES)}"
            )

        data = self._vault.get_all()

        if mode == "alpha":
            keys = sorted(data.keys())
        elif mode == "alpha_desc":
            keys = sorted(data.keys(), reverse=True)
        elif mode == "length":
            keys = sorted(data.keys(), key=len)
        elif mode == "length_desc":
            keys = sorted(data.keys(), key=len, reverse=True)
        else:  # pragma: no cover
            keys = list(data.keys())

        return {k: data[k] for k in keys}

    def group_by_prefix(self, separator: str = "_") -> Dict[str, Dict[str, str]]:
        """Group variables by their prefix (characters before the first separator).

        Args:
            separator: Character used to detect the prefix boundary.

        Returns:
            A dict mapping prefix -> {key: value}.
        """
        data = self._vault.get_all()
        groups: Dict[str, Dict[str, str]] = {}
        for key, value in sorted(data.items()):
            prefix = key.split(separator)[0] if separator in key else key
            groups.setdefault(prefix, {})[key] = value
        return groups

    def sorted_keys(self, mode: str = "alpha") -> List[str]:
        """Return only the sorted list of keys."""
        return list(self.sort(mode).keys())
