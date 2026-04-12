"""Secret detection and masking for environment variables."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class SecretError(Exception):
    """Raised when secret detection encounters an error."""


# Patterns that suggest a value is sensitive
_SENSITIVE_KEY_PATTERNS: List[re.Pattern] = [
    re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|private[_-]?key|auth|credential|access[_-]?key)"),
]

# Patterns that suggest a value looks like a secret (high entropy strings, etc.)
_SENSITIVE_VALUE_PATTERNS: List[re.Pattern] = [
    re.compile(r"^[A-Za-z0-9+/]{32,}={0,2}$"),  # base64-like
    re.compile(r"^[0-9a-fA-F]{32,}$"),            # hex strings
    re.compile(r"^sk-[A-Za-z0-9]{20,}$"),          # OpenAI-style
    re.compile(r"^ghp_[A-Za-z0-9]{36}$"),          # GitHub PAT
    re.compile(r"^xox[baprs]-[0-9A-Za-z\-]{10,}$"), # Slack tokens
]

MASK = "****"


@dataclass
class SecretScanResult:
    flagged: Dict[str, str] = field(default_factory=dict)  # key -> reason

    @property
    def has_secrets(self) -> bool:
        return bool(self.flagged)

    def summary(self) -> str:
        if not self.flagged:
            return "No secrets detected."
        lines = [f"{k}: {v}" for k, v in self.flagged.items()]
        return "Potential secrets detected:\n" + "\n".join(f"  - {l}" for l in lines)


class SecretManager:
    """Detects and masks potentially sensitive environment variable values."""

    def __init__(self, extra_key_patterns: Optional[List[str]] = None):
        self._key_patterns = list(_SENSITIVE_KEY_PATTERNS)
        if extra_key_patterns:
            for p in extra_key_patterns:
                self._key_patterns.append(re.compile(p))

    def is_sensitive_key(self, key: str) -> bool:
        return any(p.search(key) for p in self._key_patterns)

    def is_sensitive_value(self, value: str) -> bool:
        return any(p.match(value) for p in _SENSITIVE_VALUE_PATTERNS)

    def mask(self, value: str, visible_chars: int = 4) -> str:
        """Return a masked version of the value, showing only the last N chars."""
        if len(value) <= visible_chars:
            return MASK
        return MASK + value[-visible_chars:]

    def scan(self, env: Dict[str, str]) -> SecretScanResult:
        """Scan a dict of env vars and flag potentially sensitive ones."""
        result = SecretScanResult()
        for key, value in env.items():
            if self.is_sensitive_key(key):
                result.flagged[key] = "sensitive key name"
            elif self.is_sensitive_value(value):
                result.flagged[key] = "sensitive value pattern"
        return result

    def mask_all(self, env: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of env with sensitive values masked."""
        result = self.scan(env)
        masked = dict(env)
        for key in result.flagged:
            masked[key] = self.mask(env[key])
        return masked
