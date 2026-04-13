"""Tests for envault.env_cast."""

import pytest
from envault.env_cast import CastError, EnvCaster, SUPPORTED_TYPES


@pytest.fixture
def caster():
    return EnvCaster()


class TestCastStr:
    def test_str_passthrough(self, caster):
        assert caster.cast("hello", "str") == "hello"

    def test_str_numeric_stays_string(self, caster):
        assert caster.cast("42", "str") == "42"


class TestCastInt:
    def test_valid_int(self, caster):
        assert caster.cast("123", "int") == 123

    def test_negative_int(self, caster):
        assert caster.cast("-7", "int") == -7

    def test_invalid_int_raises(self, caster):
        with pytest.raises(CastError):
            caster.cast("abc", "int")


class TestCastFloat:
    def test_valid_float(self, caster):
        assert caster.cast("3.14", "float") == pytest.approx(3.14)

    def test_invalid_float_raises(self, caster):
        with pytest.raises(CastError):
            caster.cast("not_a_float", "float")


class TestCastBool:
    @pytest.mark.parametrize("value", ["true", "True", "TRUE", "1", "yes", "on"])
    def test_truthy_values(self, caster, value):
        assert caster.cast(value, "bool") is True

    @pytest.mark.parametrize("value", ["false", "False", "FALSE", "0", "no", "off"])
    def test_falsy_values(self, caster, value):
        assert caster.cast(value, "bool") is False

    def test_invalid_bool_raises(self, caster):
        with pytest.raises(CastError, match="Cannot interpret"):
            caster.cast("maybe", "bool")


class TestCastList:
    def test_comma_separated(self, caster):
        assert caster.cast("a,b,c", "list") == ["a", "b", "c"]

    def test_whitespace_stripped(self, caster):
        assert caster.cast(" x , y , z ", "list") == ["x", "y", "z"]

    def test_single_item(self, caster):
        assert caster.cast("only", "list") == ["only"]

    def test_empty_string_returns_empty_list(self, caster):
        assert caster.cast("", "list") == []


class TestUnsupportedType:
    def test_unsupported_type_raises(self, caster):
        with pytest.raises(CastError, match="Unsupported type"):
            caster.cast("value", "dict")

    def test_supported_types_constant(self):
        assert "int" in SUPPORTED_TYPES
        assert "bool" in SUPPORTED_TYPES


class TestCastAll:
    def test_cast_all_mixed_types(self, caster):
        env = {"PORT": "8080", "DEBUG": "true", "NAME": "app"}
        type_map = {"PORT": "int", "DEBUG": "bool"}
        result = caster.cast_all(env, type_map)
        assert result["PORT"] == 8080
        assert result["DEBUG"] is True
        assert result["NAME"] == "app"

    def test_cast_all_unknown_keys_default_to_str(self, caster):
        env = {"X": "42"}
        result = caster.cast_all(env, {})
        assert result["X"] == "42"
        assert isinstance(result["X"], str)
