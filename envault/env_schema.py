"""Schema validation for environment variable sets."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SchemaError(Exception):
    """Raised when schema validation fails."""


SUPPORTED_TYPES = {"string", "integer", "float", "boolean"}


class EnvSchema:
    """Manages a JSON schema that describes expected env vars."""

    def __init__(self, schema_path: str | Path) -> None:
        self._path = Path(schema_path)
        self._schema: dict[str, dict[str, Any]] = self._load()

    def _load(self) -> dict[str, dict[str, Any]]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._schema, indent=2))

    def define(self, key: str, *, type: str = "string", required: bool = True, description: str = "") -> None:
        """Add or update a key definition in the schema."""
        if type not in SUPPORTED_TYPES:
            raise SchemaError(f"Unsupported type '{type}'. Choose from {SUPPORTED_TYPES}.")
        self._schema[key] = {"type": type, "required": required, "description": description}
        self._save()

    def remove(self, key: str) -> None:
        """Remove a key from the schema."""
        if key not in self._schema:
            raise SchemaError(f"Key '{key}' not found in schema.")
        del self._schema[key]
        self._save()

    def validate(self, env: dict[str, str]) -> list[str]:
        """Validate an env dict against the schema. Returns a list of error messages."""
        errors: list[str] = []
        for key, rules in self._schema.items():
            if rules.get("required", True) and key not in env:
                errors.append(f"Missing required key: '{key}'.")
                continue
            if key not in env:
                continue
            value = env[key]
            expected_type = rules.get("type", "string")
            if not self._check_type(value, expected_type):
                errors.append(f"Key '{key}' expected type '{expected_type}', got value '{value}'.")
        return errors

    def _check_type(self, value: str, expected: str) -> bool:
        try:
            if expected == "integer":
                int(value)
            elif expected == "float":
                float(value)
            elif expected == "boolean":
                if value.lower() not in {"true", "false", "1", "0"}:
                    return False
        except ValueError:
            return False
        return True

    def list_keys(self) -> dict[str, dict[str, Any]]:
        """Return all defined schema keys."""
        return dict(self._schema)
