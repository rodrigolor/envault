"""Tests for envault.profiles.ProfileManager."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from envault.profiles import DEFAULT_PROFILE, ProfileManager


@pytest.fixture()
def mgr(tmp_path: Path) -> ProfileManager:
    return ProfileManager(tmp_path)


class TestProfileManager:
    def test_default_profile_exists_on_init(self, mgr: ProfileManager) -> None:
        assert DEFAULT_PROFILE in mgr.list_profiles()

    def test_create_profile(self, mgr: ProfileManager) -> None:
        mgr.create_profile("prod")
        assert "prod" in mgr.list_profiles()

    def test_create_duplicate_profile_raises(self, mgr: ProfileManager) -> None:
        mgr.create_profile("staging")
        with pytest.raises(ValueError, match="already exists"):
            mgr.create_profile("staging")

    def test_delete_profile(self, mgr: ProfileManager) -> None:
        mgr.create_profile("temp")
        mgr.delete_profile("temp")
        assert "temp" not in mgr.list_profiles()

    def test_delete_default_profile_raises(self, mgr: ProfileManager) -> None:
        with pytest.raises(ValueError, match="Cannot delete the default"):
            mgr.delete_profile(DEFAULT_PROFILE)

    def test_delete_nonexistent_profile_raises(self, mgr: ProfileManager) -> None:
        with pytest.raises(KeyError):
            mgr.delete_profile("ghost")

    def test_exists(self, mgr: ProfileManager) -> None:
        assert mgr.exists(DEFAULT_PROFILE)
        assert not mgr.exists("nonexistent")

    def test_vault_path_format(self, mgr: ProfileManager, tmp_path: Path) -> None:
        path = mgr.vault_path("dev")
        assert path == tmp_path / "dev.vault"

    def test_profiles_persisted_to_disk(self, tmp_path: Path) -> None:
        mgr = ProfileManager(tmp_path)
        mgr.create_profile("ci")
        # Re-load from disk
        mgr2 = ProfileManager(tmp_path)
        assert "ci" in mgr2.list_profiles()

    def test_index_file_is_valid_json(self, mgr: ProfileManager, tmp_path: Path) -> None:
        mgr.create_profile("qa")
        data = json.loads((tmp_path / ".envault_profiles.json").read_text())
        assert "profiles" in data
        assert "qa" in data["profiles"]
