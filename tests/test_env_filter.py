"""Tests for EnvFilter."""

import pytest
from envault.env_filter import EnvFilter, FilterError


class FakeVault:
    def __init__(self, data):
        self._data = data

    def get_all(self):
        return dict(self._data)


@pytest.fixture
def vault():
    return FakeVault({
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_PASSWORD": "secret",
        "APP_DEBUG": "true",
        "APP_PORT": "8080",
        "FEATURE_FLAG": "false",
        "TIMEOUT": "30",
        "RATIO": "0.75",
        "LABEL": "production",
    })


@pytest.fixture
def f(vault):
    return EnvFilter(vault)


class TestEnvFilter:
    def test_by_prefix_returns_matching(self, f):
        result = f.by_prefix("DB_")
        assert set(result.keys()) == {"DB_HOST", "DB_PORT", "DB_PASSWORD"}

    def test_by_prefix_no_match(self, f):
        result = f.by_prefix("NONEXISTENT_")
        assert result == {}

    def test_by_suffix_returns_matching(self, f):
        result = f.by_suffix("_PORT")
        assert set(result.keys()) == {"DB_PORT", "APP_PORT"}

    def test_by_suffix_no_match(self, f):
        result = f.by_suffix("_NOPE")
        assert result == {}

    def test_by_pattern_glob(self, f):
        result = f.by_pattern("DB_*")
        assert set(result.keys()) == {"DB_HOST", "DB_PORT", "DB_PASSWORD"}

    def test_by_pattern_question_mark(self, f):
        result = f.by_pattern("RATIO")
        assert "RATIO" in result

    def test_by_value_type_bool(self, f):
        result = f.by_value_type("bool")
        assert "APP_DEBUG" in result
        assert "FEATURE_FLAG" in result
        assert "LABEL" not in result

    def test_by_value_type_int(self, f):
        result = f.by_value_type("int")
        assert "DB_PORT" in result
        assert "APP_PORT" in result
        assert "TIMEOUT" in result
        assert "LABEL" not in result

    def test_by_value_type_float(self, f):
        result = f.by_value_type("float")
        assert "RATIO" in result
        assert "TIMEOUT" in result  # integers are valid floats

    def test_by_value_type_str_returns_all(self, f):
        result = f.by_value_type("str")
        assert len(result) == 9

    def test_by_value_type_invalid_raises(self, f):
        with pytest.raises(FilterError, match="Unknown type"):
            f.by_value_type("bytes")

    def test_exclude_keys(self, f):
        result = f.exclude_keys(["DB_HOST", "LABEL"])
        assert "DB_HOST" not in result
        assert "LABEL" not in result
        assert "DB_PORT" in result

    def test_only_keys_returns_subset(self, f):
        result = f.only_keys(["DB_HOST", "APP_DEBUG", "MISSING"])
        assert set(result.keys()) == {"DB_HOST", "APP_DEBUG"}

    def test_only_keys_missing_keys_ignored(self, f):
        result = f.only_keys(["DOES_NOT_EXIST"])
        assert result == {}
