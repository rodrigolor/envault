"""Compression support for vault exports and sync payloads."""

import gzip
import json
import zlib
from typing import Union


class CompressionError(Exception):
    """Raised when compression or decompression fails."""


SUPPORTED_ALGORITHMS = ("gzip", "zlib")


class CompressionManager:
    """Handles compression and decompression of vault data."""

    def __init__(self, algorithm: str = "gzip"):
        if algorithm not in SUPPORTED_ALGORITHMS:
            raise CompressionError(
                f"Unsupported algorithm '{algorithm}'. "
                f"Choose from: {SUPPORTED_ALGORITHMS}"
            )
        self.algorithm = algorithm

    def compress(self, data: Union[str, bytes]) -> bytes:
        """Compress a string or bytes payload."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        try:
            if self.algorithm == "gzip":
                return gzip.compress(data)
            elif self.algorithm == "zlib":
                return zlib.compress(data)
        except Exception as exc:
            raise CompressionError(f"Compression failed: {exc}") from exc

    def decompress(self, data: bytes) -> bytes:
        """Decompress a bytes payload."""
        try:
            if self.algorithm == "gzip":
                return gzip.decompress(data)
            elif self.algorithm == "zlib":
                return zlib.decompress(data)
        except Exception as exc:
            raise CompressionError(f"Decompression failed: {exc}") from exc

    def compress_dict(self, payload: dict) -> bytes:
        """Serialize a dict to JSON and compress it."""
        raw = json.dumps(payload, separators=(",", ":"))
        return self.compress(raw)

    def decompress_dict(self, data: bytes) -> dict:
        """Decompress bytes and deserialize JSON to a dict."""
        raw = self.decompress(data).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CompressionError(f"Failed to parse decompressed JSON: {exc}") from exc

    def ratio(self, original: Union[str, bytes], compressed: bytes) -> float:
        """Return the compression ratio (compressed / original)."""
        if isinstance(original, str):
            original = original.encode("utf-8")
        if len(original) == 0:
            return 1.0
        return len(compressed) / len(original)
