"""Tests for envault.hooks."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from envault.hooks import HookManager, HookError, HOOK_EVENTS


@pytest.fixture
def mgr(tmp_path: Path) -> HookManager:
    return HookManager(tmp_path)


class TestHookManager:
    def test_initial_hooks_empty_for_all_events(self, mgr: HookManager):
        hooks = mgr.list_hooks()
        for event in HOOK_EVENTS:
            assert event in hooks
            assert hooks[event] == []

    def test_register_hook_persists(self, tmp_path: Path):
        mgr = HookManager(tmp_path)
        mgr.register("post-set", "echo hello")
        mgr2 = HookManager(tmp_path)
        assert "echo hello" in mgr2.list_hooks("post-set")["post-set"]

    def test_register_unknown_event_raises(self, mgr: HookManager):
        with pytest.raises(HookError, match="Unknown hook event"):
            mgr.register("on-explode", "rm -rf /")

    def test_register_duplicate_not_added_twice(self, mgr: HookManager):
        mgr.register("pre-set", "echo hi")
        mgr.register("pre-set", "echo hi")
        assert mgr.list_hooks("pre-set")["pre-set"].count("echo hi") == 1

    def test_unregister_removes_hook(self, mgr: HookManager):
        mgr.register("post-get", "echo done")
        mgr.unregister("post-get", "echo done")
        assert "echo done" not in mgr.list_hooks("post-get")["post-get"]

    def test_unregister_nonexistent_raises(self, mgr: HookManager):
        with pytest.raises(HookError, match="not found"):
            mgr.unregister("post-get", "echo nope")

    def test_list_hooks_filtered_by_event(self, mgr: HookManager):
        mgr.register("pre-set", "echo a")
        mgr.register("post-set", "echo b")
        result = mgr.list_hooks("pre-set")
        assert "pre-set" in result
        assert "post-set" not in result

    def test_list_hooks_unknown_event_raises(self, mgr: HookManager):
        with pytest.raises(HookError, match="Unknown hook event"):
            mgr.list_hooks("bad-event")

    def test_run_executes_hook_and_returns_output(self, mgr: HookManager):
        mgr.register("post-set", "echo vault-updated")
        outputs = mgr.run("post-set")
        assert outputs == ["vault-updated"]

    def test_run_failing_hook_raises(self, mgr: HookManager):
        mgr.register("pre-delete", "exit 1")
        with pytest.raises(HookError, match="failed"):
            mgr.run("pre-delete")

    def test_run_unknown_event_raises(self, mgr: HookManager):
        with pytest.raises(HookError, match="Unknown hook event"):
            mgr.run("on-chaos")

    def test_run_returns_empty_when_no_hooks(self, mgr: HookManager):
        result = mgr.run("pre-get")
        assert result == []
