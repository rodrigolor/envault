"""Tests for envault.access — AccessManager."""

import pytest

from envault.access import AccessManager, AccessError


@pytest.fixture
def mgr(tmp_path):
    return AccessManager(str(tmp_path))


class TestAccessManager:
    def test_default_full_access_when_no_rules(self, mgr):
        assert mgr.can_read("MY_KEY") is True
        assert mgr.can_write("MY_KEY") is True

    def test_set_and_get_permissions(self, mgr):
        mgr.set_permissions("SECRET_*", ["read"])
        assert mgr.get_permissions("SECRET_KEY") == ["read"]

    def test_can_read_only_rule(self, mgr):
        mgr.set_permissions("READONLY_*", ["read"])
        assert mgr.can_read("READONLY_TOKEN") is True
        assert mgr.can_write("READONLY_TOKEN") is False

    def test_can_write_only_rule(self, mgr):
        mgr.set_permissions("WRITE_ONLY", ["write"])
        assert mgr.can_write("WRITE_ONLY") is True
        assert mgr.can_read("WRITE_ONLY") is False

    def test_invalid_permission_raises(self, mgr):
        with pytest.raises(AccessError, match="Invalid permissions"):
            mgr.set_permissions("*", ["execute"])

    def test_remove_permissions(self, mgr):
        mgr.set_permissions("DB_*", ["read"])
        mgr.remove_permissions("DB_*")
        # Should fall back to default full access
        assert mgr.can_write("DB_PASSWORD") is True

    def test_remove_nonexistent_pattern_raises(self, mgr):
        with pytest.raises(AccessError, match="No rules defined"):
            mgr.remove_permissions("MISSING_*")

    def test_rules_persisted_across_instances(self, tmp_path):
        m1 = AccessManager(str(tmp_path))
        m1.set_permissions("API_*", ["read"])
        m2 = AccessManager(str(tmp_path))
        assert m2.get_permissions("API_KEY") == ["read"]

    def test_list_rules_returns_all(self, mgr):
        mgr.set_permissions("A_*", ["read"])
        mgr.set_permissions("B_*", ["write"])
        rules = mgr.list_rules()
        assert "A_*" in rules
        assert "B_*" in rules

    def test_first_matching_rule_wins(self, mgr):
        mgr.set_permissions("*", ["read"])
        mgr.set_permissions("SECRET_*", ["read", "write"])
        # "*" was inserted first, so it wins for SECRET_KEY
        assert mgr.get_permissions("SECRET_KEY") == ["read"]

    def test_empty_permissions_list_is_valid(self, mgr):
        mgr.set_permissions("LOCKED", [])
        assert mgr.can_read("LOCKED") is False
        assert mgr.can_write("LOCKED") is False
