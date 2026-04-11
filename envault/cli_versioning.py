"""CLI commands for key versioning."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.versioning import VersionError, VersionManager


def _get_manager(vault_dir: str) -> VersionManager:
    return VersionManager(vault_dir)


@click.group(name="version")
def version_group() -> None:
    """Manage version history for vault keys."""


@version_group.command("list")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
def list_versions(key: str, vault_dir: str) -> None:
    """List all recorded versions of KEY."""
    mgr = _get_manager(vault_dir)
    versions = mgr.list_versions(key)
    if not versions:
        click.echo(f"No version history for '{key}'.")
        return
    for idx, entry in enumerate(versions):
        import datetime
        ts = datetime.datetime.fromtimestamp(entry["timestamp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        click.echo(f"  [{idx}] {ts}  {entry['value']}")


@version_group.command("get")
@click.argument("key")
@click.argument("index", type=int)
@click.option("--vault-dir", default=".envault", show_default=True)
def get_version(key: str, index: int, vault_dir: str) -> None:
    """Print the value of KEY at version INDEX."""
    mgr = _get_manager(vault_dir)
    try:
        value = mgr.get_version(key, index)
        click.echo(value)
    except VersionError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@version_group.command("rollback")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def rollback(key: str, vault_dir: str, password: str) -> None:
    """Roll KEY back to its previous value."""
    vault = get_vault(vault_dir, password)
    mgr = _get_manager(vault_dir)
    try:
        restored = mgr.rollback(key, vault)
        click.echo(f"Rolled back '{key}' to: {restored}")
    except VersionError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@version_group.command("clear")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
def clear_history(key: str, vault_dir: str) -> None:
    """Delete all version history for KEY."""
    mgr = _get_manager(vault_dir)
    mgr.clear(key)
    click.echo(f"Version history cleared for '{key}'.")
