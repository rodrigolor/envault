"""Tests for envault.env_lint module."""

import pytest
from envault.env_lint import EnvLinter, LintIssue, LintResult


@pytest.fixture
def linter():
    return EnvLinter()


class TestLintResult:
    def test_empty_result_has_no_errors(self):
        r = LintResult()
        assert not r.has_errors
        assert not r.has_warnings

    def test_summary_counts_correctly(self):
        r = LintResult(issues=[
            LintIssue(key="A", level="error", message="e"),
            LintIssue(key="B", level="warning", message="w"),
            LintIssue(key="C", level="warning", message="w2"),
        ])
        assert r.summary() == "1 error(s), 2 warning(s)"

    def test_str_representation(self):
        issue = LintIssue(key="MY_KEY", level="warning", message="Too long.")
        assert str(issue) == "[WARNING] MY_KEY: Too long."


class TestEnvLinter:
    def test_clean_env_has_no_issues(self, linter):
        result = linter.lint({"DATABASE_URL": "postgres://localhost/db", "PORT": "8080"})
        assert not result.issues

    def test_lowercase_key_warns(self, linter):
        result = linter.lint({"database_url": "value"})
        warnings = [i for i in result.issues if i.level == "warning" and i.key == "database_url"]
        assert len(warnings) == 1
        assert "UPPER_SNAKE_CASE" in warnings[0].message

    def test_double_underscore_warns(self, linter):
        result = linter.lint({"MY__VAR": "value"})
        keys = [i.key for i in result.issues if "consecutive" in i.message]
        assert "MY__VAR" in keys

    def test_long_key_warns(self, linter):
        long_key = "A" * 65
        result = linter.lint({long_key: "val"})
        assert any("64 characters" in i.message for i in result.issues)

    def test_placeholder_value_errors(self, linter):
        result = linter.lint({"API_KEY": "CHANGE_ME"})
        assert result.has_errors
        assert any("placeholder" in i.message.lower() for i in result.issues)

    def test_todo_placeholder_errors(self, linter):
        result = linter.lint({"SOME_VAR": "TODO"})
        assert result.has_errors

    def test_empty_sensitive_value_errors(self, linter):
        result = linter.lint({"DB_PASSWORD": ""})
        assert result.has_errors
        assert any("empty value" in i.message for i in result.issues)

    def test_empty_non_sensitive_value_is_ok(self, linter):
        result = linter.lint({"FEATURE_FLAG": ""})
        assert not result.has_errors

    def test_long_value_warns(self, linter):
        result = linter.lint({"BIG_VAR": "x" * 1025})
        assert any("1024 characters" in i.message for i in result.issues)

    def test_empty_key_errors(self, linter):
        result = linter.lint({"": "value"})
        assert result.has_errors
        assert any("empty" in i.message.lower() for i in result.issues)

    def test_multiple_issues_on_same_key(self, linter):
        result = linter.lint({"my__secret": ""})
        keys_with_issues = [i.key for i in result.issues]
        assert keys_with_issues.count("my__secret") >= 2
