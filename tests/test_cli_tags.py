"""Tests for the tag CLI commands."""

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from envault.cli_tags import tag_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_manager():
    mgr = MagicMock()
    mgr.get_tags.return_value = ["infra", "prod"]
    mgr.find_by_tag.return_value = ["DB_URL", "REDIS_URL"]
    mgr.list_all_tags.return_value = ["infra", "prod", "staging"]
    return mgr


class TestTagCLI:
    def test_add_tag_success(self, runner, mock_manager):
        with patch("envault.cli_tags._get_manager", return_value=mock_manager):
            result = runner.invoke(tag_group, ["add", "DB_URL", "infra"])
        assert result.exit_code == 0
        assert "Tagged 'DB_URL' with 'infra'" in result.output
        mock_manager.tag.assert_called_once_with("DB_URL", "infra")

    def test_add_tag_key_not_found(self, runner, mock_manager):
        from envault.tags import TagError
        mock_manager.tag.side_effect = TagError("Key 'MISSING' does not exist in vault.")
        with patch("envault.cli_tags._get_manager", return_value=mock_manager):
            result = runner.invoke(tag_group, ["add", "MISSING", "infra"])
        assert "Error" in result.output

    def test_remove_tag_success(self, runner, mock_manager):
        with patch("envault.cli_tags._get_manager", return_value=mock_manager):
            result = runner.invoke(tag_group, ["remove", "DB_URL", "infra"])
        assert result.exit_code == 0
        assert "Removed tag" in result.output

    def test_list_tags_shows_tags(self, runner, mock_manager):
        with patch("envault.cli_tags._get_manager", return_value=mock_manager):
            result = runner.invoke(tag_group, ["list", "DB_URL"])
        assert "infra" in result.output
        assert "prod" in result.output

    def test_list_tags_empty(self, runner, mock_manager):
        mock_manager.get_tags.return_value = []
        with patch("envault.cli_tags._get_manager", return_value=mock_manager):
            result = runner.invoke(tag_group, ["list", "DB_URL"])
        assert "No tags found" in result.output

    def test_find_by_tag_returns_keys(self, runner, mock_manager):
        with patch("envault.cli_tags._get_manager", return_value=mock_manager):
            result = runner.invoke(tag_group, ["find", "infra"])
        assert "DB_URL" in result.output
        assert "REDIS_URL" in result.output

    def test_find_by_tag_no_results(self, runner, mock_manager):
        mock_manager.find_by_tag.return_value = []
        with patch("envault.cli_tags._get_manager", return_value=mock_manager):
            result = runner.invoke(tag_group, ["find", "ghost"])
        assert "No keys found" in result.output

    def test_all_tags_lists_tags(self, runner, mock_manager):
        with patch("envault.cli_tags._get_manager", return_value=mock_manager):
            result = runner.invoke(tag_group, ["all"])
        assert "infra" in result.output
        assert "staging" in result.output
