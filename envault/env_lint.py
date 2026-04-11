"""Linting rules for environment variable keys and values."""

import re
from dataclasses import dataclass, field
from typing import List, Optional


class LintError(Exception):
    pass


@dataclass
class LintIssue:
    key: str
    level: str  # 'warning' or 'error'
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.key}: {self.message}"


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.level == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.level == "warning" for i in self.issues)

    def summary(self) -> str:
        errors = sum(1 for i in self.issues if i.level == "error")
        warnings = sum(1 for i in self.issues if i.level == "warning")
        return f"{errors} error(s), {warnings} warning(s)"


class EnvLinter:
    """Lints environment variable keys and values against common best-practice rules."""

    UPPERCASE_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
    DOUBLE_UNDERSCORE_RE = re.compile(r"__")
    PLACEHOLDER_RE = re.compile(r"^(CHANGE_ME|TODO|FIXME|PLACEHOLDER|YOUR_.+)$", re.IGNORECASE)
    EMPTY_VALUE_KEYS = {"SECRET", "PASSWORD", "TOKEN", "KEY", "PASS"}

    def lint(self, env: dict) -> LintResult:
        result = LintResult()
        for key, value in env.items():
            self._check_key(key, result)
            self._check_value(key, value, result)
        return result

    def _check_key(self, key: str, result: LintResult) -> None:
        if not key:
            result.issues.append(LintIssue(key="(empty)", level="error", message="Key must not be empty."))
            return
        if not self.UPPERCASE_RE.match(key):
            result.issues.append(LintIssue(key=key, level="warning",
                                            message="Key should be UPPER_SNAKE_CASE."))
        if self.DOUBLE_UNDERSCORE_RE.search(key):
            result.issues.append(LintIssue(key=key, level="warning",
                                            message="Key contains consecutive underscores."))
        if len(key) > 64:
            result.issues.append(LintIssue(key=key, level="warning",
                                            message="Key exceeds 64 characters."))

    def _check_value(self, key: str, value: str, result: LintResult) -> None:
        if self.PLACEHOLDER_RE.match(str(value)):
            result.issues.append(LintIssue(key=key, level="error",
                                            message=f"Value looks like a placeholder: '{value}'."))
        upper_key = key.upper()
        if any(s in upper_key for s in self.EMPTY_VALUE_KEYS) and not value:
            result.issues.append(LintIssue(key=key, level="error",
                                            message="Sensitive key has an empty value."))
        if isinstance(value, str) and len(value) > 1024:
            result.issues.append(LintIssue(key=key, level="warning",
                                            message="Value exceeds 1024 characters."))
