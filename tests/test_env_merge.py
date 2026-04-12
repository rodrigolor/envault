"""Tests for envault.env_merge."""

from pathlib import Path

import pytest

from envault.env_merge import EnvMerger, MergeError, MergeResult


class FakeVault:
    def __init__(self, initial=None):
        self._data = dict(initial or {})

    def get(self, key):
        return self._data.get(key)

    def get_all(self):
        return dict(self._data)

    def set(self, key, value):
        self._data[key] = value


@pytest.fixture
def vault():
    return FakeVault({"EXISTING": "old"})


@pytest.fixture
def merger(vault):
    return EnvMerger(vault)


def test_merge_adds_new_keys(merger, vault):
    result = merger.merge({"NEW_KEY": "value"})
    assert "NEW_KEY" in result.added
    assert vault.get("NEW_KEY") == "value"


def test_merge_skips_existing_without_overwrite(merger, vault):
    result = merger.merge({"EXISTING": "new_value"}, overwrite=False)
    assert "EXISTING" in result.skipped
    assert vault.get("EXISTING") == "old"


def test_merge_updates_existing_with_overwrite(merger, vault):
    result = merger.merge({"EXISTING": "new_value"}, overwrite=True)
    assert "EXISTING" in result.updated
    assert vault.get("EXISTING") == "new_value"


def test_merge_result_has_changes_when_added(merger):
    result = merger.merge({"X": "1"})
    assert result.has_changes is True


def test_merge_result_no_changes_when_all_skipped(merger, vault):
    result = merger.merge({"EXISTING": "x"}, overwrite=False)
    assert result.has_changes is False


def test_merge_result_summary_format(merger):
    result = MergeResult(added=["A", "B"], updated=["C"], skipped=["D"])
    assert "Added: 2" in result.summary()
    assert "Updated: 1" in result.summary()
    assert "Skipped: 1" in result.summary()


def test_merge_file_parses_dotenv(tmp_path, merger, vault):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nFOO=bar\nBAZ=\"quoted\"\n")
    result = merger.merge_file(env_file)
    assert "FOO" in result.added
    assert vault.get("FOO") == "bar"
    assert vault.get("BAZ") == "quoted"


def test_merge_file_not_found_raises(merger):
    with pytest.raises(MergeError, match="File not found"):
        merger.merge_file(Path("/nonexistent/.env"))


def test_merge_file_invalid_line_raises(tmp_path, merger):
    bad_file = tmp_path / "bad.env"
    bad_file.write_text("NOEQUALSSIGN\n")
    with pytest.raises(MergeError, match="Invalid line"):
        merger.merge_file(bad_file)


def test_merge_file_skips_blank_lines(tmp_path, merger):
    env_file = tmp_path / ".env"
    env_file.write_text("\n\nKEY=val\n\n")
    result = merger.merge_file(env_file)
    assert "KEY" in result.added
