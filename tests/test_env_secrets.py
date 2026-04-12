"""Tests for envault.env_secrets module."""

from __future__ import annotations

import pytest

from envault.env_secrets import MASK, SecretManager, SecretScanResult


@pytest.fixture
def manager():
    return SecretManager()


class TestSecretScanResult:
    def test_empty_result_has_no_secrets(self):
        result = SecretScanResult()
        assert not result.has_secrets

    def test_flagged_result_has_secrets(self):
        result = SecretScanResult(flagged={"API_KEY": "sensitive key name"})
        assert result.has_secrets

    def test_summary_no_secrets(self):
        result = SecretScanResult()
        assert "No secrets" in result.summary()

    def test_summary_with_secrets(self):
        result = SecretScanResult(flagged={"TOKEN": "sensitive key name"})
        summary = result.summary()
        assert "TOKEN" in summary
        assert "sensitive key name" in summary


class TestSecretManager:
    def test_sensitive_key_password(self, manager):
        assert manager.is_sensitive_key("DB_PASSWORD")

    def test_sensitive_key_token(self, manager):
        assert manager.is_sensitive_key("GITHUB_TOKEN")

    def test_sensitive_key_api_key(self, manager):
        assert manager.is_sensitive_key("STRIPE_API_KEY")

    def test_non_sensitive_key(self, manager):
        assert not manager.is_sensitive_key("APP_ENV")
        assert not manager.is_sensitive_key("PORT")

    def test_sensitive_value_hex(self, manager):
        assert manager.is_sensitive_value("a3f1b2c4d5e6f7a8b9c0d1e2f3a4b5c6")

    def test_sensitive_value_base64(self, manager):
        assert manager.is_sensitive_value("dGhpcyBpcyBhIHNlY3JldCBrZXkgdmFsdWU=")

    def test_sensitive_value_github_pat(self, manager):
        assert manager.is_sensitive_value("ghp_" + "A" * 36)

    def test_non_sensitive_value(self, manager):
        assert not manager.is_sensitive_value("production")
        assert not manager.is_sensitive_value("8080")

    def test_mask_long_value(self, manager):
        masked = manager.mask("supersecretvalue")
        assert masked.startswith(MASK)
        assert masked.endswith("alue")
        assert "supersecret" not in masked

    def test_mask_short_value(self, manager):
        assert manager.mask("abc") == MASK

    def test_scan_flags_sensitive_keys(self, manager):
        env = {"DB_PASSWORD": "hunter2", "APP_ENV": "production"}
        result = manager.scan(env)
        assert "DB_PASSWORD" in result.flagged
        assert "APP_ENV" not in result.flagged

    def test_scan_flags_sensitive_values(self, manager):
        env = {"RANDOM_VAR": "a3f1b2c4d5e6f7a8b9c0d1e2f3a4b5c6"}
        result = manager.scan(env)
        assert "RANDOM_VAR" in result.flagged

    def test_mask_all_masks_sensitive(self, manager):
        env = {"DB_PASSWORD": "supersecret", "APP_ENV": "production"}
        masked = manager.mask_all(env)
        assert masked["APP_ENV"] == "production"
        assert masked["DB_PASSWORD"] != "supersecret"
        assert MASK in masked["DB_PASSWORD"]

    def test_extra_key_patterns(self):
        mgr = SecretManager(extra_key_patterns=[r"(?i)my_custom_field"])
        assert mgr.is_sensitive_key("MY_CUSTOM_FIELD")
        assert not mgr.is_sensitive_key("UNRELATED")
