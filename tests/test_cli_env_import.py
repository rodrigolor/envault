"""Tests for CLI import commands."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_env_import import import_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_vault():
    vault = MagicMock()
    vault.get.return_value = None
    return vault


def test_import_file_success(runner, tmp_path, mock_vault):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY1=val1\nKEY2=val2\n")
    with patch("envault.cli_env_import.get_vault", return_value=mock_vault):
        result = runner.invoke(
            import_group, ["file", str(env_file), "--password", "secret"],
        )
    assert result.exit_code == 0
    assert "Imported 2 variable(s)" in result.output
    assert "KEY1" in result.output
    assert "KEY2" in result.output


def test_import_file_no_new_vars(runner, tmp_path, mock_vault):
    env_file = tmp_path / ".env"
    env_file.write_text("EXISTING=value\n")
    mock_vault.get.return_value = "already_set"
    with patch("envault.cli_env_import.get_vault", return_value=mock_vault):
        result = runner.invoke(
            import_group, ["file", str(env_file), "--password", "secret"],
        )
    assert result.exit_code == 0
    assert "No new variables" in result.output


def test_import_file_with_overwrite(runner, tmp_path, mock_vault):
    env_file = tmp_path / ".env"
    env_file.write_text("KEY=updated\n")
    mock_vault.get.return_value = "old"
    with patch("envault.cli_env_import.get_vault", return_value=mock_vault):
        result = runner.invoke(
            import_group, ["file", str(env_file), "--password", "secret", "--overwrite"],
        )
    assert result.exit_code == 0
    assert "Imported 1 variable(s)" in result.output


def test_import_file_missing_exits_nonzero(runner, mock_vault):
    with patch("envault.cli_env_import.get_vault", return_value=mock_vault):
        result = runner.invoke(
            import_group, ["file", "/no/such/file.env", "--password", "secret"],
        )
    assert result.exit_code != 0
    assert "Import error" in result.output


def test_preview_shows_variables(runner, tmp_path):
    env_file = tmp_path / "vars.json"
    env_file.write_text(json.dumps({"PREVIEW_KEY": "preview_val"}))
    result = runner.invoke(import_group, ["preview", str(env_file)])
    assert result.exit_code == 0
    assert "PREVIEW_KEY=preview_val" in result.output


def test_preview_empty_file(runner, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# only comments\n")
    result = runner.invoke(import_group, ["preview", str(env_file)])
    assert result.exit_code == 0
    assert "No variables found" in result.output
