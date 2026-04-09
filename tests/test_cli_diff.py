"""Tests for envault.cli_diff."""

import json
import os

import pytest
from click.testing import CliRunner

from envault.cli_diff import diff_group


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_vault(monkeypatch):
    class FakeVault:
        def get_all(self):
            return {"KEY_A": "alpha", "KEY_B": "beta"}

    monkeypatch.setattr("envault.cli_diff.get_vault", lambda _pw: FakeVault())
    return FakeVault()


class TestDiffCLI:
    def test_snapshot_no_changes(self, runner, mock_vault, tmp_path):
        snap = tmp_path / "snap.json"
        snap.write_text(json.dumps({"KEY_A": "alpha", "KEY_B": "beta"}))
        result = runner.invoke(
            diff_group, ["snapshot", str(snap), "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "no changes" in result.output.lower()

    def test_snapshot_shows_added_key(self, runner, mock_vault, tmp_path):
        snap = tmp_path / "snap.json"
        snap.write_text(json.dumps({"KEY_A": "alpha"}))
        result = runner.invoke(
            diff_group, ["snapshot", str(snap), "--password", "secret"]
        )
        assert result.exit_code == 0
        assert "+ KEY_B" in result.output

    def test_snapshot_json_format(self, runner, mock_vault, tmp_path):
        snap = tmp_path / "snap.json"
        snap.write_text(json.dumps({"KEY_A": "alpha"}))
        result = runner.invoke(
            diff_group,
            ["snapshot", str(snap), "--password", "secret", "--format", "json"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "added" in data
        assert "KEY_B" in data["added"]

    def test_snapshot_invalid_json_file(self, runner, mock_vault, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("not-json")
        result = runner.invoke(
            diff_group, ["snapshot", str(bad), "--password", "secret"]
        )
        assert result.exit_code != 0
        assert "Cannot read snapshot" in result.output

    def test_files_identical(self, runner, tmp_path):
        snap = tmp_path / "snap.json"
        snap.write_text(json.dumps({"K": "v"}))
        result = runner.invoke(diff_group, ["files", str(snap), str(snap)])
        assert result.exit_code == 0
        assert "identical" in result.output.lower()

    def test_files_shows_diff(self, runner, tmp_path):
        a = tmp_path / "a.json"
        b = tmp_path / "b.json"
        a.write_text(json.dumps({"X": "1"}))
        b.write_text(json.dumps({"Y": "2"}))
        result = runner.invoke(diff_group, ["files", str(a), str(b)])
        assert result.exit_code == 0
        assert "+ Y" in result.output
        assert "- X" in result.output
