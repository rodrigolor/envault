"""Tests for envault.compression."""

import pytest

from envault.compression import CompressionError, CompressionManager, SUPPORTED_ALGORITHMS


@pytest.fixture(params=SUPPORTED_ALGORITHMS)
def mgr(request):
    return CompressionManager(algorithm=request.param)


class TestCompressionManager:
    def test_unsupported_algorithm_raises(self):
        with pytest.raises(CompressionError, match="Unsupported algorithm"):
            CompressionManager(algorithm="brotli")

    def test_compress_returns_bytes(self, mgr):
        result = mgr.compress("hello world")
        assert isinstance(result, bytes)

    def test_compress_string_and_bytes_equivalent(self, mgr):
        text = "envault secret data"
        assert mgr.compress(text) == mgr.compress(text.encode("utf-8"))

    def test_roundtrip_string(self, mgr):
        original = "DATABASE_URL=postgres://localhost/mydb"
        compressed = mgr.compress(original)
        decompressed = mgr.decompress(compressed)
        assert decompressed.decode("utf-8") == original

    def test_roundtrip_bytes(self, mgr):
        original = b"\x00\x01\x02binary data"
        compressed = mgr.compress(original)
        assert mgr.decompress(compressed) == original

    def test_compress_dict_roundtrip(self, mgr):
        payload = {"API_KEY": "abc123", "DEBUG": "true", "PORT": "8080"}
        compressed = mgr.compress_dict(payload)
        result = mgr.decompress_dict(compressed)
        assert result == payload

    def test_decompress_invalid_data_raises(self, mgr):
        with pytest.raises(CompressionError, match="Decompression failed"):
            mgr.decompress(b"not valid compressed data")

    def test_decompress_dict_invalid_json_raises(self, mgr):
        # Compress something that isn't valid JSON
        bad = mgr.compress(b"not-json-at-all")
        with pytest.raises(CompressionError, match="Failed to parse decompressed JSON"):
            mgr.decompress_dict(bad)

    def test_ratio_is_float_between_zero_and_one_for_large_input(self, mgr):
        data = "KEY=VALUE\n" * 200
        compressed = mgr.compress(data)
        r = mgr.ratio(data, compressed)
        assert isinstance(r, float)
        assert r < 1.0  # large repetitive data should compress well

    def test_ratio_empty_string_returns_one(self, mgr):
        compressed = mgr.compress("")
        r = mgr.ratio("", compressed)
        assert r == 1.0

    def test_compress_empty_string(self, mgr):
        compressed = mgr.compress("")
        assert mgr.decompress(compressed) == b""

    def test_compress_dict_empty(self, mgr):
        result = mgr.decompress_dict(mgr.compress_dict({}))
        assert result == {}
