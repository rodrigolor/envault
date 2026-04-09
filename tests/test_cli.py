"""Tests for the envault CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli import cli


PASSWORD = "test-password"
VAULT_PATH = ".test-envault"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_vault():
    with patch("envault.cli.get_vault") as mock_get_vault:
        vault = MagicMock()
        mock_get_vault.return_value = vault
        yield vault


def test_set_command_success(runner, mock_vault):
    result = runner.invoke(
        cli, ["set", "MY_KEY", "my_value", "--path", VAULT_PATH, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Set 'MY_KEY' successfully" in result.output
    mock_vault.set.assert_called_once_with("MY_KEY", "my_value")


def test_get_command_success(runner, mock_vault):
    mock_vault.get.return_value = "my_value"
    result = runner.invoke(
        cli, ["get", "MY_KEY", "--path", VAULT_PATH, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "my_value" in result.output
    mock_vault.get.assert_called_once_with("MY_KEY")


def test_get_command_key_not_found(runner, mock_vault):
    mock_vault.get.return_value = None
    result = runner.invoke(
        cli, ["get", "MISSING_KEY", "--path", VAULT_PATH, "--password", PASSWORD]
    )
    assert result.exit_code == 1
    assert "not found" in result.output


def test_list_command_with_variables(runner, mock_vault):
    mock_vault.get_all.return_value = {"KEY1": "val1", "KEY2": "val2"}
    result = runner.invoke(
        cli, ["list", "--path", VAULT_PATH, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "KEY1=val1" in result.output
    assert "KEY2=val2" in result.output


def test_list_command_empty_vault(runner, mock_vault):
    mock_vault.get_all.return_value = {}
    result = runner.invoke(
        cli, ["list", "--path", VAULT_PATH, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Vault is empty" in result.output


def test_delete_command_success(runner, mock_vault):
    mock_vault.delete.return_value = True
    result = runner.invoke(
        cli, ["delete", "MY_KEY", "--path", VAULT_PATH, "--password", PASSWORD]
    )
    assert result.exit_code == 0
    assert "Deleted 'MY_KEY' successfully" in result.output
    mock_vault.delete.assert_called_once_with("MY_KEY")


def test_delete_command_key_not_found(runner, mock_vault):
    mock_vault.delete.return_value = False
    result = runner.invoke(
        cli, ["delete", "MISSING_KEY", "--path", VAULT_PATH, "--password", PASSWORD]
    )
    assert result.exit_code == 1
    assert "not found" in result.output


def test_set_command_handles_exception(runner, mock_vault):
    mock_vault.set.side_effect = ValueError("Encryption failed")
    result = runner.invoke(
        cli, ["set", "BAD_KEY", "val", "--path", VAULT_PATH, "--password", PASSWORD]
    )
    assert result.exit_code == 1
