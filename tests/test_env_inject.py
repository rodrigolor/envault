"""Tests for envault.env_inject."""

from __future__ import annotations

import pytest

from envault.env_inject import EnvInjector, InjectionError


class FakeVault:
    def __init__(self, data: dict[str, str]) -> None:
        self._data = data

    def get_all(self) -> dict[str, str]:
        return dict(self._data)


@pytest.fixture()
def vault() -> FakeVault:
    return FakeVault({"DB_URL": "postgres://localhost/db", "SECRET_KEY": "s3cr3t", "DEBUG": "true"})


@pytest.fixture()
def injector(vault: FakeVault) -> EnvInjector:
    return EnvInjector(vault)  # type: ignore[arg-type]


class TestEnvInjector:
    def test_inject_all_into_custom_target(self, injector: EnvInjector) -> None:
        target: dict = {}
        injected = injector.inject(target=target)
        assert target["DB_URL"] == "postgres://localhost/db"
        assert target["SECRET_KEY"] == "s3cr3t"
        assert target["DEBUG"] == "true"
        assert len(injected) == 3

    def test_inject_with_prefix(self, injector: EnvInjector) -> None:
        target: dict = {}
        injected = injector.inject(prefix="APP_", target=target)
        assert "APP_DB_URL" in target
        assert "APP_SECRET_KEY" in target
        assert "DB_URL" not in target
        assert len(injected) == 3

    def test_inject_does_not_overwrite_by_default(self, injector: EnvInjector) -> None:
        target: dict = {"DB_URL": "original"}
        injector.inject(target=target)
        assert target["DB_URL"] == "original"

    def test_inject_overwrites_when_flag_set(self, injector: EnvInjector) -> None:
        target: dict = {"DB_URL": "original"}
        injector.inject(overwrite=True, target=target)
        assert target["DB_URL"] == "postgres://localhost/db"

    def test_inject_specific_keys(self, injector: EnvInjector) -> None:
        target: dict = {}
        injected = injector.inject(keys=["SECRET_KEY"], target=target)
        assert "SECRET_KEY" in target
        assert "DB_URL" not in target
        assert len(injected) == 1

    def test_inject_missing_key_raises(self, injector: EnvInjector) -> None:
        with pytest.raises(InjectionError, match="MISSING_KEY"):
            injector.inject(keys=["MISSING_KEY"], target={})

    def test_eject_removes_injected_keys(self, injector: EnvInjector) -> None:
        target: dict = {}
        injector.inject(target=target)
        removed = injector.eject(target=target)
        assert len(removed) == 3
        assert target == {}

    def test_eject_with_prefix(self, injector: EnvInjector) -> None:
        target: dict = {}
        injector.inject(prefix="APP_", target=target)
        removed = injector.eject(prefix="APP_", target=target)
        assert all(k.startswith("APP_") for k in removed)
        assert target == {}

    def test_eject_ignores_keys_not_in_target(self, injector: EnvInjector) -> None:
        target: dict = {"DB_URL": "postgres://localhost/db"}
        removed = injector.eject(target=target)
        assert "DB_URL" in removed
        assert len(removed) == 1
        assert target == {}
