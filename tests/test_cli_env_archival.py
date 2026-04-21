"""Tests for the archival CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from envault.cli_env_archival import archival_group


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_manager():
    with patch("envault.cli_env_archival._get_manager") as mock:
        mgr = MagicMock()
        mock.return_value = mgr
        yield mgr


def _invoke(runner, args, obj=None):
    return runner.invoke(archival_group, args, obj=obj or {"vault_dir": ".envault"})


class TestArchivalCLI:
    def test_mark_success(self, runner: CliRunner, mock_manager: MagicMock) -> None:
        result = _invoke(runner, ["mark", "OLD_KEY"])
        mock_manager.archive.assert_called_once_with("OLD_KEY", None)
        assert "archived" in result.output
        assert result.exit_code == 0

    def test_mark_with_reason(self, runner: CliRunner, mock_manager: MagicMock) -> None:
        result = _invoke(runner, ["mark", "OLD_KEY", "--reason", "deprecated"])
        mock_manager.archive.assert_called_once_with("OLD_KEY", "deprecated")
        assert result.exit_code == 0

    def test_mark_duplicate_shows_error(self, runner: CliRunner, mock_manager: MagicMock) -> None:
        from envault.env_archival import ArchivalError
        mock_manager.archive.side_effect = ArchivalError("already archived")
        result = _invoke(runner, ["mark", "OLD_KEY"])
        assert "Error" in result.output
        assert result.exit_code == 1

    def test_unmark_success(self, runner: CliRunner, mock_manager: MagicMock) -> None:
        result = _invoke(runner, ["unmark", "OLD_KEY"])
        mock_manager.unarchive.assert_called_once_with("OLD_KEY")
        assert "unarchived" in result.output
        assert result.exit_code == 0

    def test_unmark_unknown_shows_error(self, runner: CliRunner, mock_manager: MagicMock) -> None:
        from envault.env_archival import ArchivalError
        mock_manager.unarchive.side_effect = ArchivalError("not archived")
        result = _invoke(runner, ["unmark", "GHOST"])
        assert "Error" in result.output
        assert result.exit_code == 1

    def test_list_empty(self, runner: CliRunner, mock_manager: MagicMock) -> None:
        mock_manager.list_archived.return_value = []
        result = _invoke(runner, ["list"])
        assert "No archived keys" in result.output
        assert result.exit_code == 0

    def test_list_with_keys(self, runner: CliRunner, mock_manager: MagicMock) -> None:
        mock_manager.list_archived.return_value = ["OLD_KEY"]
        mock_manager.get_info.return_value = {"archived_at": "2024-01-01T00:00:00+00:00", "reason": ""}
        result = _invoke(runner, ["list"])
        assert "OLD_KEY" in result.output
        assert result.exit_code == 0

    def test_check_archived(self, runner: CliRunner, mock_manager: MagicMock) -> None:
        mock_manager.is_archived.return_value = True
        mock_manager.get_info.return_value = {"archived_at": "2024-06-01T12:00:00+00:00", "reason": ""}
        result = _invoke(runner, ["check", "OLD_KEY"])
        assert "is archived" in result.output
        assert result.exit_code == 0

    def test_check_not_archived(self, runner: CliRunner, mock_manager: MagicMock) -> None:
        mock_manager.is_archived.return_value = False
        result = _invoke(runner, ["check", "ACTIVE_KEY"])
        assert "not archived" in result.output
        assert result.exit_code == 0
