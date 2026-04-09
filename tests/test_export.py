"""Tests for envault.export module."""

import json
import pytest
from envault.export import ExportManager


@pytest.fixture
def mgr():
    return ExportManager()


SAMPLE = {"API_KEY": "secret123", "DEBUG": "true", "PORT": "8080"}


class TestExportManager:
    def test_export_dotenv_format(self, mgr):
        output = mgr.export(SAMPLE, fmt="dotenv")
        assert 'API_KEY="secret123"' in output
        assert 'DEBUG="true"' in output
        assert 'PORT="8080"' in output

    def test_export_json_format(self, mgr):
        output = mgr.export(SAMPLE, fmt="json")
        parsed = json.loads(output)
        assert parsed == SAMPLE

    def test_export_shell_format(self, mgr):
        output = mgr.export(SAMPLE, fmt="shell")
        assert "export API_KEY='secret123'" in output
        assert "export DEBUG='true'" in output

    def test_export_unsupported_format_raises(self, mgr):
        with pytest.raises(ValueError, match="Unsupported format"):
            mgr.export(SAMPLE, fmt="xml")

    def test_import_dotenv(self, mgr):
        content = 'API_KEY="secret123"\nDEBUG="true"\nPORT="8080"\n'
        result = mgr.import_data(content, fmt="dotenv")
        assert result == SAMPLE

    def test_import_json(self, mgr):
        content = json.dumps(SAMPLE)
        result = mgr.import_data(content, fmt="json")
        assert result == SAMPLE

    def test_import_shell(self, mgr):
        content = "export API_KEY='secret123'\nexport DEBUG='true'\nexport PORT='8080'\n"
        result = mgr.import_data(content, fmt="shell")
        assert result == SAMPLE

    def test_import_dotenv_ignores_comments_and_blanks(self, mgr):
        content = "# comment\n\nFOO=bar\n"
        result = mgr.import_data(content, fmt="dotenv")
        assert result == {"FOO": "bar"}

    def test_import_json_non_dict_raises(self, mgr):
        with pytest.raises(ValueError, match="top-level object"):
            mgr.import_data("[1, 2, 3]", fmt="json")

    def test_roundtrip_dotenv(self, mgr):
        output = mgr.export(SAMPLE, fmt="dotenv")
        result = mgr.import_data(output, fmt="dotenv")
        assert result == SAMPLE

    def test_roundtrip_json(self, mgr):
        output = mgr.export(SAMPLE, fmt="json")
        result = mgr.import_data(output, fmt="json")
        assert result == SAMPLE

    def test_roundtrip_shell(self, mgr):
        output = mgr.export(SAMPLE, fmt="shell")
        result = mgr.import_data(output, fmt="shell")
        assert result == SAMPLE

    def test_export_value_with_double_quote_escaped(self, mgr):
        output = mgr.export({"KEY": 'say "hello"'}, fmt="dotenv")
        assert 'say \\"hello\\"' in output

    def test_empty_variables_export(self, mgr):
        assert mgr.export({}, fmt="dotenv") == ""
        assert mgr.export({}, fmt="shell") == ""
