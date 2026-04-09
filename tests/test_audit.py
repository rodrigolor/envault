"""Tests for the AuditLog class."""

import pytest
from pathlib import Path
from envault.audit import AuditLog


@pytest.fixture
def audit_log(tmp_path):
    return AuditLog(base_dir=str(tmp_path), profile="default")


class TestAuditLog:
    def test_record_creates_log_file(self, audit_log):
        audit_log.record(action="set", key="API_KEY", profile="default")
        assert audit_log.log_path.exists()

    def test_read_returns_empty_when_no_log(self, tmp_path):
        log = AuditLog(base_dir=str(tmp_path), profile="empty")
        assert log.read() == []

    def test_record_and_read_single_event(self, audit_log):
        audit_log.record(action="set", key="DB_URL", profile="default")
        events = audit_log.read()
        assert len(events) == 1
        assert events[0]["action"] == "set"
        assert events[0]["key"] == "DB_URL"
        assert events[0]["profile"] == "default"
        assert "timestamp" in events[0]

    def test_record_multiple_events(self, audit_log):
        audit_log.record(action="set", key="FOO", profile="default")
        audit_log.record(action="get", key="FOO", profile="default")
        audit_log.record(action="delete", key="FOO", profile="default")
        events = audit_log.read()
        assert len(events) == 3
        assert [e["action"] for e in events] == ["set", "get", "delete"]

    def test_read_with_limit(self, audit_log):
        for i in range(5):
            audit_log.record(action="set", key=f"VAR_{i}", profile="default")
        events = audit_log.read(limit=3)
        assert len(events) == 3
        assert events[-1]["key"] == "VAR_4"

    def test_record_without_key(self, audit_log):
        audit_log.record(action="list", profile="default")
        events = audit_log.read()
        assert len(events) == 1
        assert "key" not in events[0]
        assert events[0]["action"] == "list"

    def test_clear_removes_log(self, audit_log):
        audit_log.record(action="set", key="X", profile="default")
        audit_log.clear()
        assert not audit_log.log_path.exists()
        assert audit_log.read() == []

    def test_clear_on_nonexistent_log_does_not_raise(self, audit_log):
        audit_log.clear()  # should not raise

    def test_profile_isolation(self, tmp_path):
        log_a = AuditLog(base_dir=str(tmp_path), profile="prod")
        log_b = AuditLog(base_dir=str(tmp_path), profile="dev")
        log_a.record(action="set", key="PROD_KEY", profile="prod")
        assert log_b.read() == []
        assert len(log_a.read()) == 1
