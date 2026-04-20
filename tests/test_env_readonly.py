"""Tests for envault.env_readonly."""

from __future__ import annotations

import json

import pytest

from envault.env_readonly import ReadOnlyError, ReadOnlyManager


@pytest.fixture()
def mgr(tmp_path):
    return ReadOnlyManager(tmp_path)


class TestReadOnlyManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_readonly() == []

    def test_protect_key(self, mgr):
        mgr.protect("DB_PASSWORD")
        assert mgr.is_readonly("DB_PASSWORD")

    def test_protect_persists_to_disk(self, tmp_path):
        mgr = ReadOnlyManager(tmp_path)
        mgr.protect("SECRET_KEY")

        mgr2 = ReadOnlyManager(tmp_path)
        assert mgr2.is_readonly("SECRET_KEY")

    def test_protect_writes_json(self, tmp_path):
        mgr = ReadOnlyManager(tmp_path)
        mgr.protect("API_KEY")

        data = json.loads((tmp_path / "readonly.json").read_text())
        assert "API_KEY" in data["readonly"]

    def test_unprotect_removes_key(self, mgr):
        mgr.protect("TOKEN")
        mgr.unprotect("TOKEN")
        assert not mgr.is_readonly("TOKEN")

    def test_unprotect_unknown_key_raises(self, mgr):
        with pytest.raises(ReadOnlyError, match="not marked as read-only"):
            mgr.unprotect("UNKNOWN")

    def test_is_readonly_false_for_unknown(self, mgr):
        assert not mgr.is_readonly("DOES_NOT_EXIST")

    def test_list_readonly_sorted(self, mgr):
        mgr.protect("Z_KEY")
        mgr.protect("A_KEY")
        mgr.protect("M_KEY")
        assert mgr.list_readonly() == ["A_KEY", "M_KEY", "Z_KEY"]

    def test_protect_same_key_twice_is_idempotent(self, mgr):
        mgr.protect("IDEMPOTENT")
        mgr.protect("IDEMPOTENT")
        assert mgr.list_readonly().count("IDEMPOTENT") == 1

    def test_guard_raises_for_readonly_key(self, mgr):
        mgr.protect("LOCKED")
        with pytest.raises(ReadOnlyError, match="Cannot modify 'LOCKED'"):
            mgr.guard("LOCKED")

    def test_guard_custom_action_in_message(self, mgr):
        mgr.protect("LOCKED")
        with pytest.raises(ReadOnlyError, match="Cannot delete 'LOCKED'"):
            mgr.guard("LOCKED", action="delete")

    def test_guard_passes_for_unprotected_key(self, mgr):
        mgr.guard("FREE_KEY")  # should not raise
