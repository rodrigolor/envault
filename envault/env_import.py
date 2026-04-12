"""Import environment variables from external sources (.env files, shell exports, JSON)."""

import json
import re
from pathlib import Path
from typing import Dict, Optional


class ImportError(Exception):
    pass


class EnvImporter:
    """Parses and imports env vars from various file formats into a Vault."""

    SUPPORTED_FORMATS = ("dotenv", "json", "shell")

    def __init__(self, vault):
        self.vault = vault

    def import_file(self, path: str, fmt: Optional[str] = None, overwrite: bool = False) -> Dict[str, str]:
        """Import variables from a file. Returns dict of imported key-value pairs."""
        p = Path(path)
        if not p.exists():
            raise ImportError(f"File not found: {path}")

        if fmt is None:
            fmt = self._detect_format(p)

        content = p.read_text(encoding="utf-8")

        if fmt == "dotenv":
            parsed = self._parse_dotenv(content)
        elif fmt == "json":
            parsed = self._parse_json(content)
        elif fmt == "shell":
            parsed = self._parse_shell(content)
        else:
            raise ImportError(f"Unsupported format: {fmt}. Choose from {self.SUPPORTED_FORMATS}")

        imported = {}
        for key, value in parsed.items():
            if not overwrite and self.vault.get(key) is not None:
                continue
            self.vault.set(key, value)
            imported[key] = value

        return imported

    def _detect_format(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix == ".json":
            return "json"
        if suffix in (".sh", ".bash", ".zsh"):
            return "shell"
        return "dotenv"

    def _parse_dotenv(self, content: str) -> Dict[str, str]:
        result = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                result[key] = value
        return result

    def _parse_json(self, content: str) -> Dict[str, str]:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ImportError(f"Invalid JSON: {e}")
        if not isinstance(data, dict):
            raise ImportError("JSON root must be an object")
        return {str(k): str(v) for k, v in data.items()}

    def _parse_shell(self, content: str) -> Dict[str, str]:
        result = {}
        pattern = re.compile(r'^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=["\']?([^"\'\n]*)["\']?')
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = pattern.match(line)
            if m:
                result[m.group(1)] = m.group(2).strip()
        return result
