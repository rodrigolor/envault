"""Type casting for environment variable values."""

from typing import Any, Dict, Optional


class CastError(Exception):
    """Raised when a value cannot be cast to the requested type."""


SUPPORTED_TYPES = {"str", "int", "float", "bool", "list"}

_BOOL_TRUE = {"true", "1", "yes", "on"}
_BOOL_FALSE = {"false", "0", "no", "off"}


class EnvCaster:
    """Cast environment variable string values to Python types."""

    def cast(self, value: str, to_type: str) -> Any:
        """Cast *value* to *to_type*. Raises CastError on failure."""
        if to_type not in SUPPORTED_TYPES:
            raise CastError(
                f"Unsupported type '{to_type}'. Choose from: {sorted(SUPPORTED_TYPES)}"
            )
        try:
            if to_type == "str":
                return str(value)
            if to_type == "int":
                return int(value)
            if to_type == "float":
                return float(value)
            if to_type == "bool":
                return self._cast_bool(value)
            if to_type == "list":
                return self._cast_list(value)
        except CastError:
            raise
        except Exception as exc:
            raise CastError(
                f"Cannot cast '{value}' to {to_type}: {exc}"
            ) from exc

    def _cast_bool(self, value: str) -> bool:
        normalised = value.strip().lower()
        if normalised in _BOOL_TRUE:
            return True
        if normalised in _BOOL_FALSE:
            return False
        raise CastError(
            f"Cannot interpret '{value}' as bool. "
            f"Use one of: {sorted(_BOOL_TRUE | _BOOL_FALSE)}"
        )

    def _cast_list(self, value: str) -> list:
        """Split on commas; each element is stripped."""
        return [item.strip() for item in value.split(",") if item.strip()]

    def cast_all(self, env: Dict[str, str], type_map: Dict[str, str]) -> Dict[str, Any]:
        """Cast multiple values according to *type_map* {key: type}.

        Keys absent from *type_map* are returned as plain strings.
        """
        result: Dict[str, Any] = {}
        for key, value in env.items():
            to_type = type_map.get(key, "str")
            result[key] = self.cast(value, to_type)
        return result
