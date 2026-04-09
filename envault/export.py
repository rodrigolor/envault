"""Export and import environment variables in various formats."""

import json
from pathlib import Path
from typing import Dict, Optional


SUPPORTED_FORMATS = ("dotenv", "json", "shell")


class ExportManager:
    """Handles exporting and importing vault contents in different formats."""

    def export(self, variables: Dict[str, str], fmt: str = "dotenv") -> str:
        """Serialize variables to the requested format string."""
        if fmt not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")
        if fmt == "dotenv":
            return self._to_dotenv(variables)
        if fmt == "json":
            return self._to_json(variables)
        if fmt == "shell":
            return self._to_shell(variables)

    def import_data(self, content: str, fmt: str = "dotenv") -> Dict[str, str]:
        """Parse variables from a format string."""
        if fmt not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")
        if fmt == "dotenv":
            return self._from_dotenv(content)
        if fmt == "json":
            return self._from_json(content)
        if fmt == "shell":
            return self._from_shell(content)

    # -- serialisers ----------------------------------------------------------

    def _to_dotenv(self, variables: Dict[str, str]) -> str:
        lines = []
        for key, value in sorted(variables.items()):
            escaped = value.replace('"', '\\"')
            lines.append(f'{key}="{escaped}"')
        return "\n".join(lines) + ("\n" if lines else "")

    def _to_json(self, variables: Dict[str, str]) -> str:
        return json.dumps(variables, indent=2, sort_keys=True) + "\n"

    def _to_shell(self, variables: Dict[str, str]) -> str:
        lines = []
        for key, value in sorted(variables.items()):
            escaped = value.replace("'", "'\"'\"'")
            lines.append(f"export {key}='{escaped}'")
        return "\n".join(lines) + ("\n" if lines else "")

    # -- parsers --------------------------------------------------------------

    def _from_dotenv(self, content: str) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, raw_value = line.partition("=")
            value = raw_value.strip().strip('"').strip("'")
            result[key.strip()] = value
        return result

    def _from_json(self, content: str) -> Dict[str, str]:
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("JSON content must be a top-level object.")
        return {str(k): str(v) for k, v in data.items()}

    def _from_shell(self, content: str) -> Dict[str, str]:
        result: Dict[str, str] = {}
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[len("export "):]
            if not line or "=" not in line:
                continue
            key, _, raw_value = line.partition("=")
            value = raw_value.strip().strip("'")
            result[key.strip()] = value
        return result
