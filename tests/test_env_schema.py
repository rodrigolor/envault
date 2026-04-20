"""Tests for EnvSchema."""
from __future__ import annotations

import pytest
from pathlib import Path

from envault.env_schema import EnvSchema, SchemaError


@pytest.fixture()
def mgr(tmp_path: Path) -> EnvSchema:
    return EnvSchema(tmp_path / "schema.json")


class TestEnvSchema:
    def test_list_empty_initially(self, mgr: EnvSchema) -> None:
        assert mgr.list_keys() == {}

    def test_define_key_persists(self, mgr: EnvSchema, tmp_path: Path) -> None:
        mgr.define("PORT", type="integer", required=True, description="App port")
        reloaded = EnvSchema(tmp_path / "schema.json")
        keys = reloaded.list_keys()
        assert "PORT" in keys
        assert keys["PORT"]["type"] == "integer"
        assert keys["PORT"]["required"] is True

    def test_define_unsupported_type_raises(self, mgr: EnvSchema) -> None:
        with pytest.raises(SchemaError, match="Unsupported type"):
            mgr.define("KEY", type="bytes")

    def test_remove_existing_key(self, mgr: EnvSchema) -> None:
        mgr.define("DB_URL")
        mgr.remove("DB_URL")
        assert "DB_URL" not in mgr.list_keys()

    def test_remove_nonexistent_key_raises(self, mgr: EnvSchema) -> None:
        with pytest.raises(SchemaError, match="not found"):
            mgr.remove("GHOST")

    def test_validate_passes_when_all_required_present(self, mgr: EnvSchema) -> None:
        mgr.define("PORT", type="integer")
        mgr.define("HOST", type="string")
        errors = mgr.validate({"PORT": "8080", "HOST": "localhost"})
        assert errors == []

    def test_validate_fails_missing_required_key(self, mgr: EnvSchema) -> None:
        mgr.define("SECRET_KEY", required=True)
        errors = mgr.validate({})
        assert any("SECRET_KEY" in e for e in errors)

    def test_validate_optional_key_missing_is_ok(self, mgr: EnvSchema) -> None:
        mgr.define("DEBUG", type="boolean", required=False)
        errors = mgr.validate({})
        assert errors == []

    def test_validate_wrong_type_integer(self, mgr: EnvSchema) -> None:
        mgr.define("PORT", type="integer")
        errors = mgr.validate({"PORT": "not-a-number"})
        assert any("PORT" in e for e in errors)

    def test_validate_wrong_type_float(self, mgr: EnvSchema) -> None:
        mgr.define("RATIO", type="float")
        errors = mgr.validate({"RATIO": "abc"})
        assert any("RATIO" in e for e in errors)

    def test_validate_boolean_true_false(self, mgr: EnvSchema) -> None:
        mgr.define("ENABLED", type="boolean")
        assert mgr.validate({"ENABLED": "true"}) == []
        assert mgr.validate({"ENABLED": "false"}) == []
        assert mgr.validate({"ENABLED": "1"}) == []
        assert mgr.validate({"ENABLED": "0"}) == []

    def test_validate_boolean_invalid(self, mgr: EnvSchema) -> None:
        mgr.define("ENABLED", type="boolean")
        errors = mgr.validate({"ENABLED": "yes"})
        assert any("ENABLED" in e for e in errors)

    def test_extra_keys_in_env_are_ignored(self, mgr: EnvSchema) -> None:
        """Keys present in env but not in schema should not cause errors."""
        mgr.define("PORT", type="integer")
        errors = mgr.validate({"PORT": "8080", "UNTRACKED_VAR": "whatever"})
        assert errors == []

    def test_define_duplicate_key_overwrites(self, mgr: EnvSchema) -> None:
        """Re-defining an existing key should update its metadata."""
        mgr.define("PORT", type="integer", required=True)
        mgr.define("PORT", type="string", required=False)
        keys = mgr.list_keys()
        assert keys["PORT"]["type"] == "string"
        assert keys["PORT"]["required"] is False
