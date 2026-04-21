"""Compliance checking for environment variables against defined policies."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class ComplianceError(Exception):
    """Raised when a compliance operation fails."""


@dataclass
class ComplianceViolation:
    key: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"[{self.rule}] {self.key}: {self.message}"


@dataclass
class ComplianceResult:
    violations: List[ComplianceViolation] = field(default_factory=list)

    @property
    def is_compliant(self) -> bool:
        return len(self.violations) == 0

    def summary(self) -> str:
        if self.is_compliant:
            return "All checks passed. No violations found."
        return f"{len(self.violations)} violation(s) found."


class ComplianceManager:
    SUPPORTED_RULES = {"no_plaintext_secret", "key_uppercase", "no_empty_value", "max_length"}

    def __init__(self, vault_dir: str) -> None:
        self._path = Path(vault_dir) / "compliance.json"
        self._policies: Dict[str, object] = self._load()

    def _load(self) -> Dict[str, object]:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {}

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._policies, indent=2))

    def set_policy(self, rule: str, value: object) -> None:
        if rule not in self.SUPPORTED_RULES:
            raise ComplianceError(f"Unsupported rule: '{rule}'. Choose from {sorted(self.SUPPORTED_RULES)}")
        self._policies[rule] = value
        self._save()

    def remove_policy(self, rule: str) -> None:
        if rule not in self._policies:
            raise ComplianceError(f"Rule '{rule}' is not set.")
        del self._policies[rule]
        self._save()

    def list_policies(self) -> Dict[str, object]:
        return dict(self._policies)

    def check(self, variables: Dict[str, str]) -> ComplianceResult:
        result = ComplianceResult()
        secret_patterns = ["secret", "password", "passwd", "token", "apikey", "api_key", "private"]

        for key, value in variables.items():
            if "no_plaintext_secret" in self._policies and self._policies["no_plaintext_secret"]:
                if any(p in key.lower() for p in secret_patterns) and value and len(value) < 64:
                    result.violations.append(ComplianceViolation(key, "no_plaintext_secret", "Possible plaintext secret detected"))

            if "key_uppercase" in self._policies and self._policies["key_uppercase"]:
                if key != key.upper():
                    result.violations.append(ComplianceViolation(key, "key_uppercase", "Key must be uppercase"))

            if "no_empty_value" in self._policies and self._policies["no_empty_value"]:
                if value == "":
                    result.violations.append(ComplianceViolation(key, "no_empty_value", "Value must not be empty"))

            if "max_length" in self._policies:
                limit = int(self._policies["max_length"])
                if len(value) > limit:
                    result.violations.append(ComplianceViolation(key, "max_length", f"Value exceeds max length of {limit}"))

        return result
