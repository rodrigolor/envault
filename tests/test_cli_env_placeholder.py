"""Tests for envault.cli_env_placeholder."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock
from envault.cli_env_placeholder import placeholder_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_vault():
    vault = MagicMock()
    vault.get.side_effect = lambda k: {
        "BASE_URL": "https://example.com",
        "API_URL": "${BASE_URL}/api",
        "PLAIN": "hello",
    }.get(k)
    vault.get_all.return_value = {
        "BASE_URL": "https://example.com",
        "API_URL": "${BASE_URL}/api",
        "PLAIN": "hello",
    }
    return vault


class TestPlaceholderCLI:
    def test_resolve_plain_value(self, runner, mock_vault):
        result = runner.invoke(
            placeholder_group, ["resolve", "PLAIN"],
            obj={"vault": mock_vault},
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "PLAIN=hello" in result.output

    def test_resolve_with_reference(self, runner, mock_vault):
        result = runner.invoke(
            placeholder_group, ["resolve", "API_URL"],
            obj={"vault": mock_vault},
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "https://example.com/api" in result.output

    def test_resolve_missing_key(self, runner, mock_vault):
        result = runner.invoke(
            placeholder_group, ["resolve", "NONEXISTENT"],
            obj={"vault": mock_vault},
        )
        assert result.exit_code != 0
        assert "not found" in result.output

    def test_resolve_all_outputs_all_keys(self, runner, mock_vault):
        result = runner.invoke(
            placeholder_group, ["resolve-all"],
            obj={"vault": mock_vault},
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "BASE_URL=https://example.com" in result.output
        assert "PLAIN=hello" in result.output

    def test_resolve_all_resolves_placeholders(self, runner, mock_vault):
        """Ensure resolve-all expands placeholder references, not raw values."""
        result = runner.invoke(
            placeholder_group, ["resolve-all"],
            obj={"vault": mock_vault},
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "API_URL=https://example.com/api" in result.output
        assert "${BASE_URL}" not in result.output

    def test_list_refs_shows_references(self, runner, mock_vault):
        result = runner.invoke(
            placeholder_group, ["list-refs", "API_URL"],
            obj={"vault": mock_vault},
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "BASE_URL" in result.output

    def test_list_refs_no_placeholders(self, runner, mock_vault):
        result = runner.invoke(
            placeholder_group, ["list-refs", "PLAIN"],
            obj={"vault": mock_vault},
            catch_exceptions=False,
        )
        assert result.exit_code == 0
        assert "No placeholders" in result.output
