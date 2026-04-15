"""CLI commands for managing environment variable defaults."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.env_defaults import DefaultsError, DefaultsManager


def _get_manager(ctx: click.Context) -> DefaultsManager:
    vault = get_vault(ctx)
    return DefaultsManager(vault._storage._path.parent)  # type: ignore[attr-defined]


@click.group("defaults")
def defaults_group() -> None:
    """Manage default values for environment variables."""


@defaults_group.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def set_default(ctx: click.Context, key: str, value: str) -> None:
    """Register a default VALUE for KEY."""
    mgr = _get_manager(ctx)
    mgr.set_default(key, value)
    click.echo(f"Default set: {key}={value}")


@defaults_group.command("remove")
@click.argument("key")
@click.pass_context
def remove_default(ctx: click.Context, key: str) -> None:
    """Remove the default for KEY."""
    mgr = _get_manager(ctx)
    try:
        mgr.remove_default(key)
        click.echo(f"Default removed for '{key}'")
    except DefaultsError as exc:
        raise click.ClickException(str(exc)) from exc


@defaults_group.command("list")
@click.pass_context
def list_defaults(ctx: click.Context) -> None:
    """List all registered defaults."""
    mgr = _get_manager(ctx)
    defaults = mgr.list_defaults()
    if not defaults:
        click.echo("No defaults registered.")
        return
    for key, value in sorted(defaults.items()):
        click.echo(f"{key}={value}")


@defaults_group.command("apply")
@click.pass_context
def apply_defaults(ctx: click.Context) -> None:
    """Apply defaults to the vault for any missing keys."""
    vault = get_vault(ctx)
    mgr = _get_manager(ctx)
    applied = mgr.apply(vault)
    if not applied:
        click.echo("No defaults needed to be applied.")
        return
    for key, value in applied.items():
        click.echo(f"Applied: {key}={value}")
