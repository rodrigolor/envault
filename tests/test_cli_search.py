"""Tests for envault.cli_search CLI commands."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envault.cli_search import search_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_vault():
    vault = MagicMock()
    vault.get_all.return_value = {
        "DATABASE_URL": "postgres://localhost/db",
        "DATABASE_POOL": "10",
        "REDIS_URL": "redis://localhost:6379",
        "SECRET_KEY": "s3cr3t",
    }
    return vault


class TestSearchCLI:
    def test_find_glob_returns_matches(self, runner, mock_vault):
        with patch("envault.cli_search.get_vault", return_value=mock_vault):
            result = runner.invoke(
                search_group,
                ["find", "DATABASE_*", "--mode", "glob", "--password", "pw"],
            )
        assert result.exit_code == 0
        assert "DATABASE_URL" in result.output
        assert "DATABASE_POOL" in result.output
        assert "REDIS_URL" not in result.output

    def test_find_no_results(self, runner, mock_vault):
        with patch("envault.cli_search.get_vault", return_value=mock_vault):
            result = runner.invoke(
                search_group,
                ["find", "NOTHING_*", "--password", "pw"],
            )
        assert result.exit_code == 0
        assert "No matching" in result.output

    def test_find_invalid_regex_shows_error(self, runner, mock_vault):
        with patch("envault.cli_search.get_vault", return_value=mock_vault):
            result = runner.invoke(
                search_group,
                ["find", "[bad", "--mode", "regex", "--password", "pw"],
            )
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_grep_returns_value_matches(self, runner, mock_vault):
        with patch("envault.cli_search.get_vault", return_value=mock_vault):
            result = runner.invoke(
                search_group,
                ["grep", "localhost", "--password", "pw"],
            )
        assert result.exit_code == 0
        assert "DATABASE_URL" in result.output
        assert "REDIS_URL" in result.output
        assert "SECRET_KEY" not in result.output

    def test_grep_no_results(self, runner, mock_vault):
        with patch("envault.cli_search.get_vault", return_value=mock_vault):
            result = runner.invoke(
                search_group,
                ["grep", "zzznomatch", "--password", "pw"],
            )
        assert result.exit_code == 0
        assert "No matching" in result.output

    def test_keys_lists_all(self, runner, mock_vault):
        with patch("envault.cli_search.get_vault", return_value=mock_vault):
            result = runner.invoke(
                search_group,
                ["keys", "--password", "pw"],
            )
        assert result.exit_code == 0
        assert "DATABASE_URL" in result.output
        assert "SECRET_KEY" in result.output

    def test_keys_with_prefix(self, runner, mock_vault):
        with patch("envault.cli_search.get_vault", return_value=mock_vault):
            result = runner.invoke(
                search_group,
                ["keys", "--prefix", "DATABASE", "--password", "pw"],
            )
        assert result.exit_code == 0
        assert "DATABASE_URL" in result.output
        assert "REDIS_URL" not in result.output
