"""Validation rules for environment variable keys and values."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import json

VALID_KEY_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


class ValidationError(Exception):
    """Raised when a validation rule is violated."""


@dataclass
class RuleSet:
    required: List[str] = field(default_factory=list)
    pattern: Dict[str, str] = field(default_factory=dict)   # key -> regex pattern
    max_length: Dict[str, int] = field(default_factory=dict)  # key -> max chars


class EnvValidator:
    """Validates env var keys/values against configurable rules."""

    def __init__(self, rules_path: Path) -> None:
        self._path = rules_path
        self._ruleset: RuleSet = self._load()

    # ------------------------------------------------------------------
    # persistence
    # ------------------------------------------------------------------

    def _load(self) -> RuleSet:
        if not self._path.exists():
            return RuleSet()
        data = json.loads(self._path.read_text())
        return RuleSet(
            required=data.get("required", []),
            pattern=data.get("pattern", {}),
            max_length={k: int(v) for k, v in data.get("max_length", {}).items()},
        )

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(
                {
                    "required": self._ruleset.required,
                    "pattern": self._ruleset.pattern,
                    "max_length": self._ruleset.max_length,
                },
                indent=2,
            )
        )

    # ------------------------------------------------------------------
    # rule management
    # ------------------------------------------------------------------

    def add_required(self, key: str) -> None:
        if key not in self._ruleset.required:
            self._ruleset.required.append(key)
            self._save()

    def add_pattern(self, key: str, pattern: str) -> None:
        re.compile(pattern)  # raises re.error if invalid
        self._ruleset.pattern[key] = pattern
        self._save()

    def add_max_length(self, key: str, length: int) -> None:
        if length <= 0:
            raise ValidationError("max_length must be a positive integer")
        self._ruleset.max_length[key] = length
        self._save()

    # ------------------------------------------------------------------
    # validation
    # ------------------------------------------------------------------

    def validate_key(self, key: str) -> None:
        """Raise ValidationError if *key* is not a valid identifier."""
        if not VALID_KEY_RE.match(key):
            raise ValidationError(
                f"Key '{key}' is invalid. Keys must match {VALID_KEY_RE.pattern}"
            )

    def validate_value(self, key: str, value: str) -> None:
        """Raise ValidationError if *value* violates any rule for *key*."""
        if key in self._ruleset.pattern:
            if not re.fullmatch(self._ruleset.pattern[key], value):
                raise ValidationError(
                    f"Value for '{key}' does not match pattern '{self._ruleset.pattern[key]}'"
                )
        if key in self._ruleset.max_length:
            limit = self._ruleset.max_length[key]
            if len(value) > limit:
                raise ValidationError(
                    f"Value for '{key}' exceeds max length of {limit} characters"
                )

    def validate_all(self, env: Dict[str, str]) -> List[str]:
        """Return a list of error messages for *env* dict (empty = valid)."""
        errors: List[str] = []
        for key in self._ruleset.required:
            if key not in env:
                errors.append(f"Required key '{key}' is missing")
        for key, value in env.items():
            try:
                self.validate_key(key)
                self.validate_value(key, value)
            except ValidationError as exc:
                errors.append(str(exc))
        return errors
