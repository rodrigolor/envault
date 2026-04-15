"""Tests for envault.env_masking."""

from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_masking import MaskingError, MaskingManager


@pytest.fixture
def mgr(tmp_path: Path) -> MaskingManager:
    return MaskingManager(tmp_path)


class TestMaskingManager:
    def test_list_empty_initially(self, mgr: MaskingManager) -> None:
        assert mgr.list_masked() == []

    def test_mask_key(self, mgr: MaskingManager) -> None:
        mgr.mask("SECRET_KEY")
        assert mgr.is_masked("SECRET_KEY")

    def test_mask_persists_to_disk(self, tmp_path: Path) -> None:
        m1 = MaskingManager(tmp_path)
        m1.mask("DB_PASSWORD")
        m2 = MaskingManager(tmp_path)
        assert m2.is_masked("DB_PASSWORD")

    def test_mask_same_key_twice_no_duplicate(self, mgr: MaskingManager) -> None:
        mgr.mask("API_KEY")
        mgr.mask("API_KEY")
        assert mgr.list_masked().count("API_KEY") == 1

    def test_unmask_key(self, mgr: MaskingManager) -> None:
        mgr.mask("TOKEN")
        mgr.unmask("TOKEN")
        assert not mgr.is_masked("TOKEN")

    def test_unmask_nonexistent_raises(self, mgr: MaskingManager) -> None:
        with pytest.raises(MaskingError, match="not masked"):
            mgr.unmask("MISSING")

    def test_is_masked_false_for_unknown_key(self, mgr: MaskingManager) -> None:
        assert not mgr.is_masked("UNKNOWN")

    def test_apply_replaces_masked_values(self, mgr: MaskingManager) -> None:
        mgr.mask("SECRET")
        result = mgr.apply({"SECRET": "supersecret", "PUBLIC": "hello"})
        assert result["SECRET"] == MaskingManager.MASK_PLACEHOLDER
        assert result["PUBLIC"] == "hello"

    def test_apply_does_not_mutate_original(self, mgr: MaskingManager) -> None:
        mgr.mask("KEY")
        original = {"KEY": "value"}
        mgr.apply(original)
        assert original["KEY"] == "value"

    def test_apply_empty_variables(self, mgr: MaskingManager) -> None:
        assert mgr.apply({}) == {}

    def test_list_masked_returns_all(self, mgr: MaskingManager) -> None:
        for key in ["A", "B", "C"]:
            mgr.mask(key)
        assert set(mgr.list_masked()) == {"A", "B", "C"}
