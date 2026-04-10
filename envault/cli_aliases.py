"""CLI commands for managing vault key aliases."""

from __future__ import annotations

from pathlib import Path

import click

from envault.aliases import AliasError, AliasManager


def _get_manager(ctx: click.Context) -> AliasManager:
    base_dir = ctx.obj.get("base_dir", Path.home() / ".envault")
    return AliasManager(base_dir)


@click.group(name="alias")
def alias_group() -> None:
    """Manage short-hand aliases for vault keys."""


@alias_group.command("add")
@click.argument("alias")
@click.argument("key")
@click.pass_context
def add_alias(ctx: click.Context, alias: str, key: str) -> None:
    """Add a new ALIAS pointing to KEY."""
    try:
        _get_manager(ctx).add(alias, key)
        click.echo(f"Alias '{alias}' -> '{key}' created.")
    except AliasError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@alias_group.command("remove")
@click.argument("alias")
@click.pass_context
def remove_alias(ctx: click.Context, alias: str) -> None:
    """Remove an existing ALIAS."""
    try:
        _get_manager(ctx).remove(alias)
        click.echo(f"Alias '{alias}' removed.")
    except AliasError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@alias_group.command("list")
@click.pass_context
def list_aliases(ctx: click.Context) -> None:
    """List all defined aliases."""
    aliases = _get_manager(ctx).list_aliases()
    if not aliases:
        click.echo("No aliases defined.")
        return
    for alias, key in sorted(aliases.items()):
        click.echo(f"  {alias} -> {key}")


@alias_group.command("resolve")
@click.argument("alias")
@click.pass_context
def resolve_alias(ctx: click.Context, alias: str) -> None:
    """Print the vault key that ALIAS maps to."""
    key = _get_manager(ctx).resolve(alias)
    if key is None:
        click.echo(f"Alias '{alias}' not found.", err=True)
        raise SystemExit(1)
    click.echo(key)


@alias_group.command("rename")
@click.argument("old_alias")
@click.argument("new_alias")
@click.pass_context
def rename_alias(ctx: click.Context, old_alias: str, new_alias: str) -> None:
    """Rename OLD_ALIAS to NEW_ALIAS."""
    try:
        _get_manager(ctx).rename(old_alias, new_alias)
        click.echo(f"Alias '{old_alias}' renamed to '{new_alias}'.")
    except AliasError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
