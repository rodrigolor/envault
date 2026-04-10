"""Tests for envault.remotes and envault.cli_remotes."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from envault.remotes import RemoteError, RemoteManager
from envault.cli_remotes import remote_group


@pytest.fixture()
def mgr(tmp_path):
    return RemoteManager(tmp_path)


class TestRemoteManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_remotes() == []

    def test_add_and_list(self, mgr):
        mgr.add("origin", "file", "/tmp/vault")
        assert "origin" in mgr.list_remotes()

    def test_add_duplicate_raises(self, mgr):
        mgr.add("origin", "file", "/tmp/vault")
        with pytest.raises(RemoteError, match="already exists"):
            mgr.add("origin", "file", "/tmp/other")

    def test_add_unsupported_type_raises(self, mgr):
        with pytest.raises(RemoteError, match="Unsupported remote type"):
            mgr.add("bad", "ftp", "ftp://host")

    def test_get_returns_config(self, mgr):
        mgr.add("origin", "s3", "s3://my-bucket")
        info = mgr.get("origin")
        assert info["type"] == "s3"
        assert info["url"] == "s3://my-bucket"

    def test_get_missing_raises(self, mgr):
        with pytest.raises(RemoteError, match="not found"):
            mgr.get("ghost")

    def test_remove_remote(self, mgr):
        mgr.add("origin", "file", "/tmp/vault")
        mgr.remove("origin")
        assert "origin" not in mgr.list_remotes()

    def test_remove_missing_raises(self, mgr):
        with pytest.raises(RemoteError, match="not found"):
            mgr.remove("ghost")

    def test_update_remote(self, mgr):
        mgr.add("origin", "file", "/tmp/vault")
        mgr.update("origin", url="/tmp/new-vault")
        assert mgr.get("origin")["url"] == "/tmp/new-vault"

    def test_update_missing_raises(self, mgr):
        with pytest.raises(RemoteError, match="not found"):
            mgr.update("ghost", url="/x")

    def test_persists_across_instances(self, tmp_path):
        m1 = RemoteManager(tmp_path)
        m1.add("origin", "file", "/tmp/vault")
        m2 = RemoteManager(tmp_path)
        assert "origin" in m2.list_remotes()


class TestRemoteCLI:
    @pytest.fixture()
    def runner(self):
        return CliRunner()

    def test_add_and_list(self, runner, tmp_path):
        result = runner.invoke(
            remote_group,
            ["add", "origin", "--type", "file", "--url", "/tmp/v", "--base-dir", str(tmp_path)],
        )
        assert result.exit_code == 0
        assert "origin" in result.output

        result = runner.invoke(remote_group, ["list", "--base-dir", str(tmp_path)])
        assert "origin" in result.output
        assert "file" in result.output

    def test_add_duplicate_exits_nonzero(self, runner, tmp_path):
        args = ["add", "origin", "--type", "file", "--url", "/x", "--base-dir", str(tmp_path)]
        runner.invoke(remote_group, args)
        result = runner.invoke(remote_group, args)
        assert result.exit_code != 0

    def test_remove_command(self, runner, tmp_path):
        runner.invoke(
            remote_group,
            ["add", "origin", "--type", "file", "--url", "/x", "--base-dir", str(tmp_path)],
        )
        result = runner.invoke(remote_group, ["remove", "origin", "--base-dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "removed" in result.output

    def test_list_empty(self, runner, tmp_path):
        result = runner.invoke(remote_group, ["list", "--base-dir", str(tmp_path)])
        assert "No remotes" in result.output
