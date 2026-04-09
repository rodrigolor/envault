"""Tests for envault.cli_templates."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch

from envault.cli_templates import template_group
from envault.templates import TemplateError


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def mock_manager():
    with patch("envault.cli_templates._get_manager") as mock:
        manager = MagicMock()
        mock.return_value = manager
        yield manager


@pytest.fixture()
def mock_vault():
    with patch("envault.cli_templates.get_vault") as mock:
        vault = MagicMock()
        vault.get_all.return_value = {"FOO": "bar", "BAZ": "qux"}
        mock.return_value = vault
        yield vault


class TestTemplateCLI:
    def test_list_shows_templates(self, runner, mock_manager):
        mock_manager.list_templates.return_value = ["dev", "prod"]
        result = runner.invoke(template_group, ["list"])
        assert result.exit_code == 0
        assert "dev" in result.output
        assert "prod" in result.output

    def test_list_empty_message(self, runner, mock_manager):
        mock_manager.list_templates.return_value = []
        result = runner.invoke(template_group, ["list"])
        assert result.exit_code == 0
        assert "No templates found" in result.output

    def test_delete_success(self, runner, mock_manager):
        result = runner.invoke(template_group, ["delete", "old"])
        assert result.exit_code == 0
        assert "deleted" in result.output
        mock_manager.delete_template.assert_called_once_with("old")

    def test_delete_not_found(self, runner, mock_manager):
        mock_manager.delete_template.side_effect = TemplateError("does not exist")
        result = runner.invoke(template_group, ["delete", "ghost"])
        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_apply_success(self, runner, mock_manager, mock_vault):
        mock_manager.apply_template.return_value = 3
        result = runner.invoke(
            template_group, ["apply", "prod", "--vault-dir", ".ev"],
            input="secret\nsecret\n",
        )
        assert result.exit_code == 0
        assert "3 variable(s) written" in result.output

    def test_apply_template_not_found(self, runner, mock_manager, mock_vault):
        mock_manager.apply_template.side_effect = TemplateError("does not exist")
        result = runner.invoke(
            template_group, ["apply", "missing", "--vault-dir", ".ev"],
            input="secret\nsecret\n",
        )
        assert result.exit_code != 0
        assert "does not exist" in result.output
