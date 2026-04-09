"""Tests for envault.templates."""

from __future__ import annotations

import pytest

from envault.templates import TemplateError, TemplateManager


class FakeVault:
    def __init__(self, data=None):
        self._data = dict(data or {})

    def get_all(self):
        return dict(self._data)

    def set(self, key, value):
        self._data[key] = value


@pytest.fixture()
def mgr(tmp_path):
    return TemplateManager(tmp_path)


class TestTemplateManager:
    def test_list_empty_on_init(self, mgr):
        assert mgr.list_templates() == []

    def test_save_and_list(self, mgr):
        mgr.save_template("base", {"FOO": "bar"})
        assert "base" in mgr.list_templates()

    def test_load_returns_correct_variables(self, mgr):
        mgr.save_template("prod", {"DB_URL": "postgres://", "PORT": "5432"})
        result = mgr.load_template("prod")
        assert result == {"DB_URL": "postgres://", "PORT": "5432"}

    def test_load_nonexistent_raises(self, mgr):
        with pytest.raises(TemplateError, match="does not exist"):
            mgr.load_template("ghost")

    def test_delete_removes_template(self, mgr):
        mgr.save_template("tmp", {"X": "1"})
        mgr.delete_template("tmp")
        assert "tmp" not in mgr.list_templates()

    def test_delete_nonexistent_raises(self, mgr):
        with pytest.raises(TemplateError, match="does not exist"):
            mgr.delete_template("nope")

    def test_save_empty_name_raises(self, mgr):
        with pytest.raises(TemplateError, match="must not be empty"):
            mgr.save_template("", {"A": "1"})

    def test_apply_writes_to_vault(self, mgr):
        mgr.save_template("dev", {"ENV": "development", "DEBUG": "true"})
        vault = FakeVault()
        count = mgr.apply_template("dev", vault)
        assert count == 2
        assert vault.get_all() == {"ENV": "development", "DEBUG": "true"}

    def test_apply_nonexistent_raises(self, mgr):
        vault = FakeVault()
        with pytest.raises(TemplateError):
            mgr.apply_template("missing", vault)

    def test_persistence_across_instances(self, tmp_path):
        m1 = TemplateManager(tmp_path)
        m1.save_template("shared", {"KEY": "value"})
        m2 = TemplateManager(tmp_path)
        assert m2.load_template("shared") == {"KEY": "value"}

    def test_overwrite_existing_template(self, mgr):
        mgr.save_template("cfg", {"A": "1"})
        mgr.save_template("cfg", {"B": "2"})
        assert mgr.load_template("cfg") == {"B": "2"}
