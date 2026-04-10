"""CLI commands for managing pinned vault keys."""

from __future__ import annotations

from pathlib import Path

import click

from envault.pinning import PinError, PinManager


def _get_manager(ctx: click.Context) -> PinManager:
    vault_dir = ctx.obj.get("vault_dir", Path.home() / ".envault")
    return PinManager(vault_dir)


@click.group("pin")
def pin_group() -> None:
    """Pin keys to protect them from accidental overwrites."""


@pin_group.command("add")
@click.argument("key")
@click.pass_context
def add_pin(ctx: click.Context, key: str) -> None:
    """Pin KEY so it cannot be overwritten."""
    mgr = _get_manager(ctx)
    try:
        mgr.pin(key)
        click.echo(f"Pinned '{key}'.")
    except PinError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@pin_group.command("remove")
@click.argument("key")
@click.pass_context
def remove_pin(ctx: click.Context, key: str) -> None:
    """Unpin KEY to allow modifications again."""
    mgr = _get_manager(ctx)
    try:
        mgr.unpin(key)
        click.echo(f"Unpinned '{key}'.")
    except PinError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@pin_group.command("list")
@click.pass_context
def list_pins(ctx: click.Context) -> None:
    """List all currently pinned keys."""
    mgr = _get_manager(ctx)
    pins = mgr.list_pins()
    if not pins:
        click.echo("No keys are pinned.")
    else:
        for key in pins:
            click.echo(f"  📌 {key}")


@pin_group.command("check")
@click.argument("key")
@click.pass_context
def check_pin(ctx: click.Context, key: str) -> None:
    """Check whether KEY is pinned."""
    mgr = _get_manager(ctx)
    if mgr.is_pinned(key):
        click.echo(f"'{key}' is pinned.")
    else:
        click.echo(f"'{key}' is not pinned.")
