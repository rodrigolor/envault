"""Tests for EnvImporter."""

import json
import pytest
from pathlib import Path
from envault.env_import import EnvImporter, ImportError as EnvImportError


class FakeVault:
    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def set(self, key, value):
        self._store[key] = value


@pytest.fixture
def vault():
    return FakeVault()


@pytest.fixture
def importer(vault):
    return EnvImporter(vault)


def test_import_dotenv_basic(tmp_path, importer, vault):
    f = tmp_path / ".env"
    f.write_text("FOO=bar\nBAZ=qux\n")
    result = importer.import_file(str(f))
    assert result == {"FOO": "bar", "BAZ": "qux"}
    assert vault.get("FOO") == "bar"


def test_import_dotenv_skips_comments_and_blanks(tmp_path, importer):
    f = tmp_path / ".env"
    f.write_text("# comment\n\nKEY=value\n")
    result = importer.import_file(str(f))
    assert list(result.keys()) == ["KEY"]


def test_import_dotenv_strips_quotes(tmp_path, importer):
    f = tmp_path / ".env"
    f.write_text('QUOTED="hello world"\nSINGLE=\'hi\'\n')
    result = importer.import_file(str(f))
    assert result["QUOTED"] == "hello world"
    assert result["SINGLE"] == "hi"


def test_import_json(tmp_path, importer, vault):
    f = tmp_path / "vars.json"
    f.write_text(json.dumps({"DB_HOST": "localhost", "PORT": "5432"}))
    result = importer.import_file(str(f))
    assert result["DB_HOST"] == "localhost"
    assert vault.get("PORT") == "5432"


def test_import_json_invalid_raises(tmp_path, importer):
    f = tmp_path / "bad.json"
    f.write_text("not json")
    with pytest.raises(EnvImportError, match="Invalid JSON"):
        importer.import_file(str(f))


def test_import_json_non_object_raises(tmp_path, importer):
    f = tmp_path / "list.json"
    f.write_text(json.dumps(["a", "b"]))
    with pytest.raises(EnvImportError, match="object"):
        importer.import_file(str(f))


def test_import_shell(tmp_path, importer):
    f = tmp_path / "env.sh"
    f.write_text("export APP_ENV=production\nSECRET=abc123\n")
    result = importer.import_file(str(f))
    assert result["APP_ENV"] == "production"
    assert result["SECRET"] == "abc123"


def test_overwrite_false_skips_existing(tmp_path, vault, importer):
    vault.set("FOO", "original")
    f = tmp_path / ".env"
    f.write_text("FOO=new_value\n")
    result = importer.import_file(str(f), overwrite=False)
    assert result == {}
    assert vault.get("FOO") == "original"


def test_overwrite_true_replaces_existing(tmp_path, vault, importer):
    vault.set("FOO", "original")
    f = tmp_path / ".env"
    f.write_text("FOO=new_value\n")
    result = importer.import_file(str(f), overwrite=True)
    assert result["FOO"] == "new_value"
    assert vault.get("FOO") == "new_value"


def test_missing_file_raises(importer):
    with pytest.raises(EnvImportError, match="File not found"):
        importer.import_file("/nonexistent/.env")


def test_unsupported_format_raises(tmp_path, importer):
    f = tmp_path / "vars.xml"
    f.write_text("<root/>")
    with pytest.raises(EnvImportError, match="Unsupported format"):
        importer.import_file(str(f), fmt="xml")


def test_format_auto_detected_from_extension(tmp_path, importer):
    f = tmp_path / "vars.json"
    f.write_text(json.dumps({"AUTO": "detected"}))
    result = importer.import_file(str(f))
    assert result["AUTO"] == "detected"
