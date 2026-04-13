"""Tests for envault.env_placeholder."""

import pytest
from envault.env_placeholder import PlaceholderResolver, PlaceholderError


class FakeVault:
    def __init__(self, data: dict):
        self._data = data

    def get(self, key):
        return self._data.get(key)

    def get_all(self):
        return dict(self._data)


@pytest.fixture
def vault():
    return FakeVault({
        "BASE_URL": "https://example.com",
        "API_URL": "${BASE_URL}/api",
        "FULL_URL": "${API_URL}/v1",
        "PLAIN": "hello",
        "SELF_REF": "${SELF_REF}",
    })


@pytest.fixture
def resolver(vault):
    return PlaceholderResolver(vault)


class TestPlaceholderResolver:
    def test_plain_value_unchanged(self, resolver):
        assert resolver.resolve("hello") == "hello"

    def test_single_placeholder_resolved(self, resolver):
        result = resolver.resolve("${BASE_URL}/path")
        assert result == "https://example.com/path"

    def test_nested_placeholder_resolved(self, resolver):
        result = resolver.resolve("${API_URL}/v1")
        assert result == "https://example.com/api/v1"

    def test_deeply_nested_resolved(self, resolver):
        result = resolver.resolve("${FULL_URL}")
        assert result == "https://example.com/api/v1"

    def test_missing_key_raises(self, resolver):
        with pytest.raises(PlaceholderError, match="MISSING"):
            resolver.resolve("${MISSING}")

    def test_circular_reference_raises(self, resolver):
        with pytest.raises(PlaceholderError, match="Circular"):
            resolver.resolve("${SELF_REF}")

    def test_resolve_all_returns_dict(self, resolver, vault):
        result = resolver.resolve_all({"PLAIN": "hello", "API_URL": "${BASE_URL}/api"})
        assert result["PLAIN"] == "hello"
        assert result["API_URL"] == "https://example.com/api"

    def test_has_placeholders_true(self, resolver):
        assert resolver.has_placeholders("${FOO}") is True

    def test_has_placeholders_false(self, resolver):
        assert resolver.has_placeholders("just-a-value") is False

    def test_list_references_empty(self, resolver):
        assert resolver.list_references("no refs here") == []

    def test_list_references_multiple(self, resolver):
        refs = resolver.list_references("${FOO}:${BAR}")
        assert refs == ["FOO", "BAR"]

    def test_max_depth_exceeded_raises(self):
        deep = FakeVault({"A": "${B}", "B": "${A}"})
        r = PlaceholderResolver(deep)
        with pytest.raises(PlaceholderError, match="depth"):
            r.resolve("${A}")
