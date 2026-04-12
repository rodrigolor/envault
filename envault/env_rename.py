"""Rename environment variable keys in the vault."""

from typing import Optional


class RenameError(Exception):
    pass


class RenameManager:
    def __init__(self, vault):
        self._vault = vault

    def rename(self, old_key: str, new_key: str, overwrite: bool = False) -> None:
        """Rename old_key to new_key in the vault."""
        all_vars = self._vault.get_all()

        if old_key not in all_vars:
            raise RenameError(f"Key '{old_key}' does not exist in the vault.")

        if new_key in all_vars and not overwrite:
            raise RenameError(
                f"Key '{new_key}' already exists. Use overwrite=True to replace it."
            )

        value = all_vars[old_key]
        self._vault.set(new_key, value)
        self._vault.delete(old_key)

    def bulk_rename(self, mapping: dict, overwrite: bool = False) -> dict:
        """Rename multiple keys at once. Returns a dict of {old: new} for successful renames."""
        results = {}
        errors = {}

        for old_key, new_key in mapping.items():
            try:
                self.rename(old_key, new_key, overwrite=overwrite)
                results[old_key] = new_key
            except RenameError as e:
                errors[old_key] = str(e)

        if errors:
            raise RenameError(
                f"Some renames failed: {errors}. Successful: {results}"
            )

        return results

    def preview_rename(self, old_key: str, new_key: str) -> dict:
        """Preview what a rename would do without applying it."""
        all_vars = self._vault.get_all()
        issues = []

        if old_key not in all_vars:
            issues.append(f"Source key '{old_key}' does not exist.")

        if new_key in all_vars:
            issues.append(f"Target key '{new_key}' already exists (use overwrite=True).")

        return {
            "old_key": old_key,
            "new_key": new_key,
            "value": all_vars.get(old_key),
            "target_exists": new_key in all_vars,
            "issues": issues,
            "safe": len(issues) == 0,
        }
