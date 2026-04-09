"""Tests for envault sync module."""

import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from envault.sync import FileSyncBackend, SyncManager


@pytest.fixture
def tmp_remote(tmp_path):
    return tmp_path / "remote"


@pytest.fixture
def tmp_local(tmp_path):
    return tmp_path / "local"


@pytest.fixture
def file_backend(tmp_remote):
    return FileSyncBackend(str(tmp_remote))


@pytest.fixture
def sync_manager(file_backend):
    return SyncManager(file_backend, remote_path="vault.enc")


def test_push_uploads_file(sync_manager, tmp_local, tmp_remote):
    local_file = tmp_local / "vault.enc"
    local_file.parent.mkdir(parents=True, exist_ok=True)
    local_file.write_bytes(b"encrypted-data")

    result = sync_manager.push(str(local_file))

    assert result is True
    assert (tmp_remote / "vault.enc").read_bytes() == b"encrypted-data"


def test_push_returns_false_if_local_missing(sync_manager, tmp_local):
    missing = tmp_local / "nonexistent.enc"
    result = sync_manager.push(str(missing))
    assert result is False


def test_pull_downloads_file(sync_manager, tmp_local, tmp_remote):
    remote_file = tmp_remote / "vault.enc"
    remote_file.parent.mkdir(parents=True, exist_ok=True)
    remote_file.write_bytes(b"remote-data")

    local_file = tmp_local / "vault.enc"
    result = sync_manager.pull(str(local_file))

    assert result is True
    assert local_file.read_bytes() == b"remote-data"


def test_pull_returns_false_if_remote_missing(sync_manager, tmp_local):
    local_file = tmp_local / "vault.enc"
    result = sync_manager.pull(str(local_file))
    assert result is False
    assert not local_file.exists()


def test_remote_exists_true(sync_manager, tmp_remote):
    (tmp_remote / "vault.enc").write_bytes(b"data")
    assert sync_manager.remote_exists() is True


def test_remote_exists_false(sync_manager):
    assert sync_manager.remote_exists() is False


def test_roundtrip_push_pull(sync_manager, tmp_local, tmp_path):
    local_src = tmp_local / "vault.enc"
    local_src.parent.mkdir(parents=True, exist_ok=True)
    local_src.write_bytes(b"secret-vault-bytes")

    sync_manager.push(str(local_src))

    local_dst = tmp_path / "restored" / "vault.enc"
    sync_manager.pull(str(local_dst))

    assert local_dst.read_bytes() == b"secret-vault-bytes"
