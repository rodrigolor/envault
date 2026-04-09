"""Tests for the rotation CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from envault.cli_rotation import rotation_group
from envault.crypto import CryptoManager
from envault.storage import LocalStorageBackend


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def vault_dir(tmp_path: Path) -> Path:
    data = {"KEY": "value"}
    crypto = CryptoManager("old-pass")
    ciphertext = crypto.encrypt(json.dumps(data))
    storage = LocalStorageBackend(tmp_path)
    storage.save(ciphertext)
    return tmp_path


class TestRotationCLI:
    def test_run_rotation_success(self, runner, vault_dir):
        result = runner.invoke(
            rotation_group,
            ["run", "--vault-path", str(vault_dir),
             "--old-password", "old-pass",
             "--new-password", "new-pass"],
        )
        assert result.exit_code == 0
        assert "rotation complete" in result.output
        assert "1 variable(s)" in result.output

    def test_run_rotation_wrong_old_password(self, runner, vault_dir):
        result = runner.invoke(
            rotation_group,
            ["run", "--vault-path", str(vault_dir),
             "--old-password", "wrong",
             "--new-password", "new-pass"],
        )
        assert result.exit_code != 0
        assert "Error" in result.output

    def test_check_rotation_recommends_when_no_audit(self, runner, tmp_path):
        result = runner.invoke(
            rotation_group,
            ["check", "--vault-path", str(tmp_path)],
        )
        assert result.exit_code == 0
        assert "recommended" in result.output

    def test_check_rotation_ok_after_recent_rotation(self, runner, vault_dir):
        runner.invoke(
            rotation_group,
            ["run", "--vault-path", str(vault_dir),
             "--old-password", "old-pass",
             "--new-password", "new-pass"],
        )
        result = runner.invoke(
            rotation_group,
            ["check", "--vault-path", str(vault_dir), "--max-age", "90"],
        )
        assert result.exit_code == 0
        assert "acceptable" in result.output
