"""CLI commands for searching vault variables."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.search import SearchError, SearchManager


@click.group(name="search")
def search_group() -> None:
    """Search and filter environment variables."""


@search_group.command("find")
@click.argument("pattern")
@click.option(
    "--mode",
    default="glob",
    show_default=True,
    type=click.Choice(["glob", "regex", "prefix"]),
    help="Pattern matching mode.",
)
@click.option("--profile", default="default", show_default=True, help="Profile to use.")
@click.password_option("--password", prompt="Master password", confirmation_prompt=False)
def find(pattern: str, mode: str, profile: str, password: str) -> None:
    """Find variables whose keys match PATTERN."""
    vault = get_vault(profile, password)
    manager = SearchManager(vault)
    try:
        results = manager.search(pattern, mode=mode)
    except SearchError as exc:
        raise click.ClickException(str(exc))

    if not results:
        click.echo("No matching variables found.")
        return

    for key, value in sorted(results.items()):
        click.echo(f"{key}={value}")


@search_group.command("grep")
@click.argument("substring")
@click.option("--profile", default="default", show_default=True, help="Profile to use.")
@click.password_option("--password", prompt="Master password", confirmation_prompt=False)
def grep(substring: str, profile: str, password: str) -> None:
    """Find variables whose values contain SUBSTRING."""
    vault = get_vault(profile, password)
    manager = SearchManager(vault)
    results = manager.filter_by_value(substring)

    if not results:
        click.echo("No matching variables found.")
        return

    for key, value in sorted(results.items()):
        click.echo(f"{key}={value}")


@search_group.command("keys")
@click.option("--prefix", default=None, help="Filter keys by prefix.")
@click.option("--profile", default="default", show_default=True, help="Profile to use.")
@click.password_option("--password", prompt="Master password", confirmation_prompt=False)
def keys(prefix: str, profile: str, password: str) -> None:
    """List variable keys, optionally filtered by prefix."""
    vault = get_vault(profile, password)
    manager = SearchManager(vault)
    key_list = manager.list_keys(prefix=prefix)

    if not key_list:
        click.echo("No variables found.")
        return

    for key in key_list:
        click.echo(key)
