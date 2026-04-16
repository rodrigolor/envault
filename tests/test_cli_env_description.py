"""Tests for CLI description commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_env_description import description_group
from envault.env_description import DescriptionError


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_manager():
    return MagicMock()


def _invoke(runner, args, manager):
    with patch("envault.cli_env_description._get_manager", return_value=manager):
        return runner.invoke(description_group, args)


class TestDescriptionCLI:
    def test_set_description_success(self, runner, mock_manager):
        result = _invoke(runner, ["set", "DB_URL", "Database URL"], mock_manager)
        mock_manager.set.assert_called_once_with("DB_URL", "Database URL")
        assert "Description set for 'DB_URL'" in result.output

    def test_set_description_error(self, runner, mock_manager):
        mock_manager.set.side_effect = DescriptionError("Key must not be empty.")
        result = _invoke(runner, ["set", "", "desc"], mock_manager)
        assert "Error" in result.output

    def test_get_description_found(self, runner, mock_manager):
        mock_manager.get.return_value = "My description"
        result = _invoke(runner, ["get", "API_KEY"], mock_manager)
        assert "API_KEY: My description" in result.output

    def test_get_description_not_found(self, runner, mock_manager):
        mock_manager.get.return_value = None
        result = _invoke(runner, ["get", "MISSING"], mock_manager)
        assert "No description for 'MISSING'" in result.output

    def test_remove_success(self, runner, mock_manager):
        result = _invoke(runner, ["remove", "OLD_KEY"], mock_manager)
        mock_manager.remove.assert_called_once_with("OLD_KEY")
        assert "removed" in result.output

    def test_remove_error(self, runner, mock_manager):
        mock_manager.remove.side_effect = DescriptionError("No description found for key: X")
        result = _invoke(runner, ["remove", "X"], mock_manager)
        assert "Error" in result.output

    def test_list_empty(self, runner, mock_manager):
        mock_manager.list_all.return_value = {}
        result = _invoke(runner, ["list"], mock_manager)
        assert "No descriptions defined" in result.output

    def test_list_with_entries(self, runner, mock_manager):
        mock_manager.list_all.return_value = {"FOO": "foo desc", "BAR": "bar desc"}
        result = _invoke(runner, ["list"], mock_manager)
        assert "FOO: foo desc" in result.output
        assert "BAR: bar desc" in result.output
