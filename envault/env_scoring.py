"""env_scoring.py — Score environment variable health based on metadata quality.

Assigns a health score to each key based on the presence of metadata such as
descriptions, schemas, required flags, ownership, expiry, and deprecation status.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class ScoringError(Exception):
    """Raised when scoring encounters an unrecoverable error."""


@dataclass
class KeyScore:
    """Holds the health score and breakdown for a single environment key."""

    key: str
    score: int  # 0-100
    max_score: int
    breakdown: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        if self.max_score == 0:
            return 0.0
        return round((self.score / self.max_score) * 100, 1)

    @property
    def grade(self) -> str:
        p = self.percentage
        if p >= 90:
            return "A"
        if p >= 75:
            return "B"
        if p >= 60:
            return "C"
        if p >= 40:
            return "D"
        return "F"

    def __str__(self) -> str:
        return f"{self.key}: {self.score}/{self.max_score} ({self.percentage}%) [{self.grade}]"


class EnvScorer:
    """Scores environment variable keys based on metadata completeness.

    Each criterion contributes a fixed number of points toward the total score.
    Missing metadata generates warnings to guide the user.
    """

    # Points awarded per criterion
    CRITERIA: dict[str, int] = {
        "has_description": 20,
        "has_schema": 20,
        "has_owner": 15,
        "has_required_flag": 15,
        "has_expiry": 10,
        "not_deprecated": 10,
        "has_category": 10,
    }

    def __init__(self, vault_dir: str | Path) -> None:
        self._dir = Path(vault_dir)
        self._load_managers()

    def _load_managers(self) -> None:
        """Lazily import and instantiate metadata managers."""
        from envault.env_description import DescriptionManager
        from envault.env_schema import EnvSchema
        from envault.env_ownership import OwnershipManager
        from envault.env_required import RequiredManager
        from envault.env_expiry import ExpiryManager
        from envault.env_deprecation import DeprecationManager
        from envault.env_category import CategoryManager

        self._desc = DescriptionManager(self._dir)
        self._schema = EnvSchema(self._dir)
        self._owner = OwnershipManager(self._dir)
        self._required = RequiredManager(self._dir)
        self._expiry = ExpiryManager(self._dir)
        self._deprecation = DeprecationManager(self._dir)
        self._category = CategoryManager(self._dir)

    def score_key(self, key: str) -> KeyScore:
        """Compute the health score for a single environment variable key."""
        breakdown: dict[str, int] = {}
        warnings: list[str] = []
        total = 0
        max_score = sum(self.CRITERIA.values())

        # Description
        if self._desc.get(key) is not None:
            breakdown["has_description"] = self.CRITERIA["has_description"]
            total += self.CRITERIA["has_description"]
        else:
            breakdown["has_description"] = 0
            warnings.append("Missing description")

        # Schema definition
        schema_keys = [s["key"] for s in self._schema.list()]
        if key in schema_keys:
            breakdown["has_schema"] = self.CRITERIA["has_schema"]
            total += self.CRITERIA["has_schema"]
        else:
            breakdown["has_schema"] = 0
            warnings.append("No schema/type defined")

        # Ownership
        if self._owner.get_owner(key) is not None:
            breakdown["has_owner"] = self.CRITERIA["has_owner"]
            total += self.CRITERIA["has_owner"]
        else:
            breakdown["has_owner"] = 0
            warnings.append("No owner assigned")

        # Required flag
        if key in self._required.list():
            breakdown["has_required_flag"] = self.CRITERIA["has_required_flag"]
            total += self.CRITERIA["has_required_flag"]
        else:
            breakdown["has_required_flag"] = 0
            warnings.append("Not marked as required or optional")

        # Expiry
        if self._expiry.get(key) is not None:
            breakdown["has_expiry"] = self.CRITERIA["has_expiry"]
            total += self.CRITERIA["has_expiry"]
        else:
            breakdown["has_expiry"] = 0
            warnings.append("No expiry date set")

        # Not deprecated (reward for being actively maintained)
        if not self._deprecation.is_deprecated(key):
            breakdown["not_deprecated"] = self.CRITERIA["not_deprecated"]
            total += self.CRITERIA["not_deprecated"]
        else:
            breakdown["not_deprecated"] = 0
            warnings.append("Key is deprecated")

        # Category
        if self._category.get(key) is not None:
            breakdown["has_category"] = self.CRITERIA["has_category"]
            total += self.CRITERIA["has_category"]
        else:
            breakdown["has_category"] = 0
            warnings.append("No category assigned")

        return KeyScore(
            key=key,
            score=total,
            max_score=max_score,
            breakdown=breakdown,
            warnings=warnings,
        )

    def score_all(self, keys: list[str]) -> list[KeyScore]:
        """Score all provided keys, sorted by score descending."""
        scores = [self.score_key(k) for k in keys]
        return sorted(scores, key=lambda s: s.score, reverse=True)

    def average_score(self, keys: list[str]) -> float:
        """Return the average percentage score across all keys."""
        if not keys:
            return 0.0
        scores = self.score_all(keys)
        return round(sum(s.percentage for s in scores) / len(scores), 1)
