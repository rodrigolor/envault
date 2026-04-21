"""Tests for envault.env_compliance module."""

from __future__ import annotations

import pytest

from envault.env_compliance import (
    ComplianceError,
    ComplianceManager,
    ComplianceResult,
    ComplianceViolation,
)


@pytest.fixture
def mgr(tmp_path):
    return ComplianceManager(str(tmp_path))


class TestComplianceViolation:
    def test_str_representation(self):
        v = ComplianceViolation(key="SECRET", rule="no_plaintext_secret", message="Possible plaintext secret detected")
        assert "no_plaintext_secret" in str(v)
        assert "SECRET" in str(v)


class TestComplianceResult:
    def test_empty_result_is_compliant(self):
        result = ComplianceResult()
        assert result.is_compliant is True

    def test_result_with_violations_not_compliant(self):
        v = ComplianceViolation("KEY", "key_uppercase", "msg")
        result = ComplianceResult(violations=[v])
        assert result.is_compliant is False

    def test_summary_no_violations(self):
        assert "passed" in ComplianceResult().summary()

    def test_summary_with_violations(self):
        v = ComplianceViolation("K", "r", "m")
        result = ComplianceResult(violations=[v])
        assert "1" in result.summary()


class TestComplianceManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_policies() == {}

    def test_set_and_list_policy(self, mgr):
        mgr.set_policy("key_uppercase", True)
        assert mgr.list_policies()["key_uppercase"] is True

    def test_set_persists_to_disk(self, tmp_path):
        m = ComplianceManager(str(tmp_path))
        m.set_policy("no_empty_value", True)
        m2 = ComplianceManager(str(tmp_path))
        assert m2.list_policies()["no_empty_value"] is True

    def test_set_unsupported_rule_raises(self, mgr):
        with pytest.raises(ComplianceError, match="Unsupported rule"):
            mgr.set_policy("nonexistent_rule", True)

    def test_remove_policy(self, mgr):
        mgr.set_policy("key_uppercase", True)
        mgr.remove_policy("key_uppercase")
        assert "key_uppercase" not in mgr.list_policies()

    def test_remove_nonexistent_raises(self, mgr):
        with pytest.raises(ComplianceError, match="not set"):
            mgr.remove_policy("key_uppercase")

    def test_check_uppercase_violation(self, mgr):
        mgr.set_policy("key_uppercase", True)
        result = mgr.check({"lowercase_key": "value"})
        assert not result.is_compliant
        assert any(v.rule == "key_uppercase" for v in result.violations)

    def test_check_no_empty_value_violation(self, mgr):
        mgr.set_policy("no_empty_value", True)
        result = mgr.check({"MY_KEY": ""})
        assert not result.is_compliant

    def test_check_max_length_violation(self, mgr):
        mgr.set_policy("max_length", 5)
        result = mgr.check({"KEY": "toolongvalue"})
        assert not result.is_compliant

    def test_check_no_plaintext_secret(self, mgr):
        mgr.set_policy("no_plaintext_secret", True)
        result = mgr.check({"DB_PASSWORD": "hunter2"})
        assert not result.is_compliant

    def test_check_passes_when_no_policies(self, mgr):
        result = mgr.check({"lowercase": "", "LONG": "x" * 1000})
        assert result.is_compliant

    def test_check_uppercase_passes_for_valid_key(self, mgr):
        mgr.set_policy("key_uppercase", True)
        result = mgr.check({"MY_KEY": "value"})
        assert result.is_compliant
