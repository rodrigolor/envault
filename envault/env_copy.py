"""env_copy.py — Copy or duplicate environment variable keys within a vault."""

from typing import Optional


class CopyError(Exception):
    pass


class EnvCopier:
    """Copies or duplicates env variable keys within a vault."""

    def __init__(self, vault):
        self._vault = vault

    def copy(self, source_key: str, dest_key: str, overwrite: bool = False) -> None:
        """Copy the value of source_key to dest_key."""
        all_vars = self._vault.get_all()

        if source_key not in all_vars:
            raise CopyError(f"Source key '{source_key}' does not exist.")

        if dest_key in all_vars and not overwrite:
            raise CopyError(
                f"Destination key '{dest_key}' already exists. Use overwrite=True to replace it."
            )

        self._vault.set(dest_key, all_vars[source_key])

    def bulk_copy(self, mapping: dict, overwrite: bool = False) -> dict:
        """Copy multiple keys. mapping is {source: dest}.
        Returns a dict of {dest_key: 'copied' | 'skipped'} results.
        """
        results = {}
        all_vars = self._vault.get_all()

        for source_key, dest_key in mapping.items():
            if source_key not in all_vars:
                raise CopyError(f"Source key '{source_key}' does not exist.")
            if dest_key in all_vars and not overwrite:
                results[dest_key] = "skipped"
            else:
                self._vault.set(dest_key, all_vars[source_key])
                results[dest_key] = "copied"

        return results

    def duplicate(self, key: str, suffix: str = "_COPY") -> str:
        """Duplicate a key with an auto-generated name using suffix.
        Returns the new key name.
        """
        all_vars = self._vault.get_all()

        if key not in all_vars:
            raise CopyError(f"Key '{key}' does not exist.")

        new_key = f"{key}{suffix}"
        counter = 1
        while new_key in all_vars:
            new_key = f"{key}{suffix}_{counter}"
            counter += 1

        self._vault.set(new_key, all_vars[key])
        return new_key
