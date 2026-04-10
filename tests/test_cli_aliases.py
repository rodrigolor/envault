"""CLI tests for envault alias commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.cli_aliases import alias_group
from envault.aliases import AliasManager


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def base_dir(tmp_path):
    return tmp_path


def invoke(runner, base_dir, *args):
    return runner.invoke(
        alias_group, list(args), obj={"base_dir": base_dir}, catch_exceptions=False
    )


class TestAliasCLI:
    def test_add_alias_success(self, runner, base_dir):
        result = invoke(runner, base_dir, "add", "db", "DATABASE_URL")
        assert result.exit_code == 0
        assert "created" in result.output

    def test_add_duplicate_alias_fails(self, runner, base_dir):
        invoke(runner, base_dir, "add", "db", "DATABASE_URL")
        result = invoke(runner, base_dir, "add", "db", "OTHER")
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_list_shows_aliases(self, runner, base_dir):
        invoke(runner, base_dir, "add", "db", "DATABASE_URL")
        invoke(runner, base_dir, "add", "token", "API_TOKEN")
        result = invoke(runner, base_dir, "list")
        assert "db" in result.output
        assert "token" in result.output

    def test_list_empty_message(self, runner, base_dir):
        result = invoke(runner, base_dir, "list")
        assert "No aliases" in result.output

    def test_resolve_known_alias(self, runner, base_dir):
        invoke(runner, base_dir, "add", "db", "DATABASE_URL")
        result = invoke(runner, base_dir, "resolve", "db")
        assert result.exit_code == 0
        assert "DATABASE_URL" in result.output

    def test_resolve_unknown_alias_fails(self, runner, base_dir):
        result = invoke(runner, base_dir, "resolve", "ghost")
        assert result.exit_code == 1

    def test_remove_alias_success(self, runner, base_dir):
        invoke(runner, base_dir, "add", "db", "DATABASE_URL")
        result = invoke(runner, base_dir, "remove", "db")
        assert result.exit_code == 0
        assert "removed" in result.output

    def test_rename_alias_success(self, runner, base_dir):
        invoke(runner, base_dir, "add", "db", "DATABASE_URL")
        result = invoke(runner, base_dir, "rename", "db", "database")
        assert result.exit_code == 0
        assert "renamed" in result.output
        resolve = invoke(runner, base_dir, "resolve", "database")
        assert "DATABASE_URL" in resolve.output
