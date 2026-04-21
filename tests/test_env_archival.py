"""Tests for ArchivalManager."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_archival import ArchivalError, ArchivalManager


@pytest.fixture
def mgr(tmp_path: Path) -> ArchivalManager:
    return ArchivalManager(tmp_path)


class TestArchivalManager:
    def test_list_empty_initially(self, mgr: ArchivalManager) -> None:
        assert mgr.list_archived() == []

    def test_archive_key(self, mgr: ArchivalManager) -> None:
        mgr.archive("OLD_API_KEY")
        assert mgr.is_archived("OLD_API_KEY")

    def test_archive_persists_to_disk(self, tmp_path: Path) -> None:
        mgr1 = ArchivalManager(tmp_path)
        mgr1.archive("LEGACY_URL")
        mgr2 = ArchivalManager(tmp_path)
        assert mgr2.is_archived("LEGACY_URL")

    def test_archive_with_reason(self, mgr: ArchivalManager) -> None:
        mgr.archive("DEPRECATED_KEY", reason="replaced by NEW_KEY")
        info = mgr.get_info("DEPRECATED_KEY")
        assert info is not None
        assert info["reason"] == "replaced by NEW_KEY"

    def test_archive_duplicate_raises(self, mgr: ArchivalManager) -> None:
        mgr.archive("KEY")
        with pytest.raises(ArchivalError, match="already archived"):
            mgr.archive("KEY")

    def test_unarchive_key(self, mgr: ArchivalManager) -> None:
        mgr.archive("KEY")
        mgr.unarchive("KEY")
        assert not mgr.is_archived("KEY")

    def test_unarchive_unknown_raises(self, mgr: ArchivalManager) -> None:
        with pytest.raises(ArchivalError, match="not archived"):
            mgr.unarchive("GHOST_KEY")

    def test_list_archived_sorted(self, mgr: ArchivalManager) -> None:
        mgr.archive("ZEBRA")
        mgr.archive("ALPHA")
        mgr.archive("MIDDLE")
        assert mgr.list_archived() == ["ALPHA", "MIDDLE", "ZEBRA"]

    def test_get_info_returns_none_for_unknown(self, mgr: ArchivalManager) -> None:
        assert mgr.get_info("UNKNOWN") is None

    def test_archived_at_is_recorded(self, mgr: ArchivalManager) -> None:
        mgr.archive("TIMED_KEY")
        info = mgr.get_info("TIMED_KEY")
        assert info is not None
        assert "archived_at" in info
        assert info["archived_at"]  # non-empty string
