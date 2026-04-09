"""Tests for the profile CLI sub-group."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_profiles import profile_group


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def base_dir(tmp_path: Path) -> str:
    return str(tmp_path)


class TestProfileCLI:
    def test_list_shows_default(self, runner: CliRunner, base_dir: str) -> None:
        result = runner.invoke(profile_group, ["--base-dir", base_dir, "list"])
        assert result.exit_code == 0
        assert "default" in result.output

    def test_create_profile(self, runner: CliRunner, base_dir: str) -> None:
        result = runner.invoke(profile_group, ["--base-dir", base_dir, "create", "prod"])
        assert result.exit_code == 0
        assert "created" in result.output

    def test_create_duplicate_exits_nonzero(self, runner: CliRunner, base_dir: str) -> None:
        runner.invoke(profile_group, ["--base-dir", base_dir, "create", "dup"])
        result = runner.invoke(profile_group, ["--base-dir", base_dir, "create", "dup"])
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_delete_profile(self, runner: CliRunner, base_dir: str) -> None:
        runner.invoke(profile_group, ["--base-dir", base_dir, "create", "staging"])
        result = runner.invoke(profile_group, ["--base-dir", base_dir, "delete", "staging"])
        assert result.exit_code == 0
        assert "deleted" in result.output

    def test_delete_default_exits_nonzero(self, runner: CliRunner, base_dir: str) -> None:
        result = runner.invoke(profile_group, ["--base-dir", base_dir, "delete", "default"])
        assert result.exit_code != 0

    def test_list_shows_created_profile(self, runner: CliRunner, base_dir: str) -> None:
        runner.invoke(profile_group, ["--base-dir", base_dir, "create", "ci"])
        result = runner.invoke(profile_group, ["--base-dir", base_dir, "list"])
        assert "ci" in result.output

    def test_delete_nonexistent_exits_nonzero(self, runner: CliRunner, base_dir: str) -> None:
        result = runner.invoke(profile_group, ["--base-dir", base_dir, "delete", "ghost"])
        assert result.exit_code != 0
