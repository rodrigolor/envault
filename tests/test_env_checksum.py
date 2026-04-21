"""Tests for ChecksumManager."""

import pytest
from pathlib import Path
from envault.env_checksum import ChecksumManager, ChecksumError


@pytest.fixture
def mgr(tmp_path):
    return ChecksumManager(str(tmp_path))


class TestChecksumManager:
    def test_list_empty_initially(self, mgr):
        assert mgr.list_all() == {}

    def test_has_checksum_false_initially(self, mgr):
        assert not mgr.has_checksum("MY_KEY")

    def test_record_returns_sha256_hex(self, mgr):
        digest = mgr.record("KEY", "value")
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_record_persists_to_disk(self, mgr, tmp_path):
        mgr.record("KEY", "value")
        mgr2 = ChecksumManager(str(tmp_path))
        assert mgr2.has_checksum("KEY")

    def test_verify_returns_true_for_matching_value(self, mgr):
        mgr.record("KEY", "hello")
        assert mgr.verify("KEY", "hello") is True

    def test_verify_returns_false_for_changed_value(self, mgr):
        mgr.record("KEY", "hello")
        assert mgr.verify("KEY", "world") is False

    def test_verify_raises_for_unknown_key(self, mgr):
        with pytest.raises(ChecksumError, match="No checksum recorded"):
            mgr.verify("MISSING", "value")

    def test_remove_deletes_entry(self, mgr):
        mgr.record("KEY", "val")
        mgr.remove("KEY")
        assert not mgr.has_checksum("KEY")

    def test_remove_raises_for_unknown_key(self, mgr):
        with pytest.raises(ChecksumError, match="No checksum recorded"):
            mgr.remove("MISSING")

    def test_list_all_returns_all_keys(self, mgr):
        mgr.record("A", "1")
        mgr.record("B", "2")
        result = mgr.list_all()
        assert set(result.keys()) == {"A", "B"}

    def test_same_value_same_digest(self, mgr):
        d1 = mgr.record("K1", "same")
        d2 = mgr.record("K2", "same")
        assert d1 == d2

    def test_different_values_different_digests(self, mgr):
        d1 = mgr.record("K1", "foo")
        d2 = mgr.record("K2", "bar")
        assert d1 != d2

    def test_list_all_returns_copy(self, mgr):
        mgr.record("X", "v")
        result = mgr.list_all()
        result["Y"] = "tampered"
        assert "Y" not in mgr.list_all()
