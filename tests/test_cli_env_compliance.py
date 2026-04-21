"""Tests for CLI compliance commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envault.cli_env_compliance import compliance_group
from envault.env_compliance import ComplianceError, ComplianceResult, ComplianceViolation


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_manager():
    with patch("envault.cli_env_compliance._get_manager") as mock:
        mgr = MagicMock()
        mock.return_value = mgr
        yield mgr


def _invoke(runner, *args, obj=None):
    return runner.invoke(compliance_group, args, obj=obj or {"vault_dir": "/tmp/test"})


class TestComplianceCLI:
    def test_set_policy_success(self, runner, mock_manager):
        result = _invoke(runner, "set", "key_uppercase", "true")
        assert result.exit_code == 0
        mock_manager.set_policy.assert_called_once_with("key_uppercase", True)
        assert "set to" in result.output

    def test_set_policy_numeric(self, runner, mock_manager):
        result = _invoke(runner, "set", "max_length", "128")
        assert result.exit_code == 0
        mock_manager.set_policy.assert_called_once_with("max_length", 128)

    def test_set_policy_error(self, runner, mock_manager):
        mock_manager.set_policy.side_effect = ComplianceError("Unsupported rule")
        result = _invoke(runner, "set", "bad_rule", "true")
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_remove_policy_success(self, runner, mock_manager):
        result = _invoke(runner, "remove", "key_uppercase")
        assert result.exit_code == 0
        mock_manager.remove_policy.assert_called_once_with("key_uppercase")
        assert "removed" in result.output

    def test_remove_policy_error(self, runner, mock_manager):
        mock_manager.remove_policy.side_effect = ComplianceError("not set")
        result = _invoke(runner, "remove", "key_uppercase")
        assert result.exit_code == 1

    def test_list_policies_empty(self, runner, mock_manager):
        mock_manager.list_policies.return_value = {}
        result = _invoke(runner, "list")
        assert result.exit_code == 0
        assert "No compliance" in result.output

    def test_list_policies_with_data(self, runner, mock_manager):
        mock_manager.list_policies.return_value = {"key_uppercase": True, "max_length": 128}
        result = _invoke(runner, "list")
        assert result.exit_code == 0
        assert "key_uppercase" in result.output
        assert "max_length" in result.output

    def test_check_compliant(self, runner, mock_manager):
        mock_manager.check.return_value = ComplianceResult()
        with patch("envault.cli_env_compliance.get_vault") as mock_vault_fn:
            vault = MagicMock()
            vault.get_all.return_value = {"KEY": "val"}
            mock_vault_fn.return_value = vault
            result = _invoke(runner, "check")
        assert result.exit_code == 0
        assert "passed" in result.output

    def test_check_violations(self, runner, mock_manager):
        violations = [ComplianceViolation("key", "key_uppercase", "Key must be uppercase")]
        mock_manager.check.return_value = ComplianceResult(violations=violations)
        with patch("envault.cli_env_compliance.get_vault") as mock_vault_fn:
            vault = MagicMock()
            vault.get_all.return_value = {"key": "val"}
            mock_vault_fn.return_value = vault
            result = _invoke(runner, "check")
        assert result.exit_code == 1
        assert "violation" in result.output
