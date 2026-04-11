"""Tests for envault.env_validate."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_validate import EnvValidator, ValidationError


@pytest.fixture
def validator(tmp_path: Path) -> EnvValidator:
    return EnvValidator(tmp_path / "rules.json")


class TestKeyValidation:
    def test_valid_key_passes(self, validator: EnvValidator) -> None:
        validator.validate_key("MY_VAR")
        validator.validate_key("_PRIVATE")
        validator.validate_key("CamelCase123")

    def test_key_starting_with_digit_fails(self, validator: EnvValidator) -> None:
        with pytest.raises(ValidationError, match="invalid"):
            validator.validate_key("1INVALID")

    def test_key_with_hyphen_fails(self, validator: EnvValidator) -> None:
        with pytest.raises(ValidationError):
            validator.validate_key("MY-VAR")

    def test_empty_key_fails(self, validator: EnvValidator) -> None:
        with pytest.raises(ValidationError):
            validator.validate_key("")


class TestPatternRule:
    def test_value_matching_pattern_passes(self, validator: EnvValidator) -> None:
        validator.add_pattern("PORT", r"\d{1,5}")
        validator.validate_value("PORT", "8080")

    def test_value_not_matching_pattern_fails(self, validator: EnvValidator) -> None:
        validator.add_pattern("PORT", r"\d{1,5}")
        with pytest.raises(ValidationError, match="pattern"):
            validator.validate_value("PORT", "not-a-port")

    def test_invalid_regex_raises(self, validator: EnvValidator) -> None:
        with pytest.raises(Exception):
            validator.add_pattern("KEY", "[unclosed")

    def test_pattern_persists_after_reload(self, tmp_path: Path) -> None:
        path = tmp_path / "rules.json"
        v1 = EnvValidator(path)
        v1.add_pattern("ENV", r"(prod|staging|dev)")
        v2 = EnvValidator(path)
        with pytest.raises(ValidationError):
            v2.validate_value("ENV", "unknown")


class TestMaxLengthRule:
    def test_value_within_limit_passes(self, validator: EnvValidator) -> None:
        validator.add_max_length("TOKEN", 32)
        validator.validate_value("TOKEN", "a" * 32)

    def test_value_exceeding_limit_fails(self, validator: EnvValidator) -> None:
        validator.add_max_length("TOKEN", 10)
        with pytest.raises(ValidationError, match="max length"):
            validator.validate_value("TOKEN", "a" * 11)

    def test_zero_length_rule_raises(self, validator: EnvValidator) -> None:
        with pytest.raises(ValidationError):
            validator.add_max_length("KEY", 0)


class TestValidateAll:
    def test_missing_required_key_reported(self, validator: EnvValidator) -> None:
        validator.add_required("DATABASE_URL")
        errors = validator.validate_all({"PORT": "5432"})
        assert any("DATABASE_URL" in e for e in errors)

    def test_all_required_present_no_errors(self, validator: EnvValidator) -> None:
        validator.add_required("DB")
        errors = validator.validate_all({"DB": "postgres://localhost/mydb"})
        assert errors == []

    def test_pattern_violation_included_in_errors(self, validator: EnvValidator) -> None:
        validator.add_pattern("LOG_LEVEL", r"(DEBUG|INFO|WARNING|ERROR)")
        errors = validator.validate_all({"LOG_LEVEL": "verbose"})
        assert len(errors) == 1
        assert "LOG_LEVEL" in errors[0]

    def test_multiple_violations_all_reported(self, validator: EnvValidator) -> None:
        validator.add_required("SECRET")
        validator.add_pattern("PORT", r"\d+")
        errors = validator.validate_all({"PORT": "abc"})
        assert len(errors) == 2
