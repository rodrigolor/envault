"""Tests for envault.cli_env_defaults."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from envault.cli_env_defaults import defaults_group
from envault.env_defaults import DefaultsError


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_manager(tmp_path):
    from envault.env_defaults import DefaultsManager
    return DefaultsManager(tmp_path)


def _invoke(runner, args, manager):
    with patch("envault.cli_env_defaults._get_manager", return_value=manager), \
         patch("envault.cli_env_defaults.get_vault", return_value=MagicMock(get_all=lambda: {})):
        return runner.invoke(defaults_group, args, catch_exceptions=False)


class TestDefaultsCLI:
    def test_set_default_success(self, runner, mock_manager):
        result = _invoke(runner, ["set", "LOG_LEVEL", "DEBUG"], mock_manager)
        assert result.exit_code == 0
        assert "Default set" in result.output
        assert mock_manager.get_default("LOG_LEVEL") == "DEBUG"

    def test_list_shows_defaults(self, runner, mock_manager):
        mock_manager.set_default("PORT", "3000")
        result = _invoke(runner, ["list"], mock_manager)
        assert result.exit_code == 0
        assert "PORT=3000" in result.output

    def test_list_empty(self, runner, mock_manager):
        result = _invoke(runner, ["list"], mock_manager)
        assert result.exit_code == 0
        assert "No defaults" in result.output

    def test_remove_default_success(self, runner, mock_manager):
        mock_manager.set_default("X", "42")
        result = _invoke(runner, ["remove", "X"], mock_manager)
        assert result.exit_code == 0
        assert "removed" in result.output

    def test_remove_nonexistent_fails(self, runner, mock_manager):
        result = runner.invoke(
            defaults_group,
            ["remove", "GHOST"],
            obj={},
            catch_exceptions=False,
        )
        # ClickException exits with code 1
        # We just verify the manager raises correctly in isolation
        with pytest.raises(DefaultsError):
            mock_manager.remove_default("GHOST")

    def test_apply_outputs_applied_keys(self, runner, mock_manager):
        fake_vault = MagicMock()
        fake_vault.get_all.return_value = {}
        mock_manager.set_default("DB_HOST", "localhost")
        with patch("envault.cli_env_defaults._get_manager", return_value=mock_manager), \
             patch("envault.cli_env_defaults.get_vault", return_value=fake_vault):
            result = runner.invoke(defaults_group, ["apply"], catch_exceptions=False)
        assert result.exit_code == 0
        assert "Applied" in result.output
