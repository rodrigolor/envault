"""Filter environment variables by various criteria."""

from fnmatch import fnmatch
from typing import Dict, List, Optional


class FilterError(Exception):
    pass


class EnvFilter:
    """Filter vault variables by prefix, suffix, pattern, or value type."""

    def __init__(self, vault):
        self._vault = vault

    def by_prefix(self, prefix: str) -> Dict[str, str]:
        """Return all variables whose keys start with the given prefix."""
        all_vars = self._vault.get_all()
        return {k: v for k, v in all_vars.items() if k.startswith(prefix)}

    def by_suffix(self, suffix: str) -> Dict[str, str]:
        """Return all variables whose keys end with the given suffix."""
        all_vars = self._vault.get_all()
        return {k: v for k, v in all_vars.items() if k.endswith(suffix)}

    def by_pattern(self, pattern: str) -> Dict[str, str]:
        """Return all variables whose keys match a glob pattern."""
        all_vars = self._vault.get_all()
        return {k: v for k, v in all_vars.items() if fnmatch(k, pattern)}

    def by_value_type(self, value_type: str) -> Dict[str, str]:
        """Return variables whose values match a loose type: bool, int, float, or str."""
        valid_types = {"bool", "int", "float", "str"}
        if value_type not in valid_types:
            raise FilterError(f"Unknown type '{value_type}'. Choose from: {sorted(valid_types)}")

        all_vars = self._vault.get_all()
        result = {}
        for k, v in all_vars.items():
            if value_type == "bool" and v.lower() in ("true", "false", "1", "0", "yes", "no"):
                result[k] = v
            elif value_type == "int":
                try:
                    int(v)
                    result[k] = v
                except ValueError:
                    pass
            elif value_type == "float":
                try:
                    float(v)
                    result[k] = v
                except ValueError:
                    pass
            elif value_type == "str":
                result[k] = v
        return result

    def exclude_keys(self, keys: List[str]) -> Dict[str, str]:
        """Return all variables except those with the specified keys."""
        all_vars = self._vault.get_all()
        exclude = set(keys)
        return {k: v for k, v in all_vars.items() if k not in exclude}

    def only_keys(self, keys: List[str]) -> Dict[str, str]:
        """Return only the variables with the specified keys (if they exist)."""
        all_vars = self._vault.get_all()
        return {k: all_vars[k] for k in keys if k in all_vars}
