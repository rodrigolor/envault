"""CLI commands for managing deprecated environment variable keys."""

from __future__ import annotations

import click

from envault.env_deprecation import DeprecationManager, DeprecationError


def _get_manager(ctx: click.Context) -> DeprecationManager:
    vault_dir = ctx.obj.get("vault_dir", ".")
    return DeprecationManager(vault_dir)


@click.group("deprecation")
def deprecation_group() -> None:
    """Manage deprecated environment variable keys."""


@deprecation_group.command("mark")
@click.argument("key")
@click.option("--reason", default="", help="Reason for deprecation.")
@click.option("--replacement", default=None, help="Suggested replacement key.")
@click.pass_context
def mark_deprecated(ctx: click.Context, key: str, reason: str, replacement: str | None) -> None:
    """Mark a key as deprecated."""
    mgr = _get_manager(ctx)
    try:
        mgr.mark_deprecated(key, reason=reason, replacement=replacement)
        click.echo(f"Key '{key}' marked as deprecated.")
    except DeprecationError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@deprecation_group.command("unmark")
@click.argument("key")
@click.pass_context
def unmark_deprecated(ctx: click.Context, key: str) -> None:
    """Remove the deprecated status from a key."""
    mgr = _get_manager(ctx)
    try:
        mgr.unmark_deprecated(key)
        click.echo(f"Key '{key}' is no longer deprecated.")
    except DeprecationError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@deprecation_group.command("list")
@click.pass_context
def list_deprecated(ctx: click.Context) -> None:
    """List all deprecated keys."""
    mgr = _get_manager(ctx)
    entries = mgr.list_deprecated()
    if not entries:
        click.echo("No deprecated keys.")
        return
    for key, info in entries.items():
        line = f"  {key}"
        if info.get("reason"):
            line += f" — {info['reason']}"
        if info.get("replacement"):
            line += f" (use: {info['replacement']})"
        click.echo(line)


@deprecation_group.command("check")
@click.argument("key")
@click.pass_context
def check_key(ctx: click.Context, key: str) -> None:
    """Check whether a key is deprecated and display a warning if so."""
    mgr = _get_manager(ctx)
    msg = mgr.warn_if_deprecated(key)
    if msg:
        click.echo(msg)
    else:
        click.echo(f"Key '{key}' is not deprecated.")
