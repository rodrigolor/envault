"""CLI commands for managing archived environment variable keys."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_archival import ArchivalError, ArchivalManager


def _get_manager(ctx: click.Context) -> ArchivalManager:
    vault_dir = ctx.obj.get("vault_dir", ".envault")
    return ArchivalManager(vault_dir)


@click.group("archive")
def archival_group() -> None:
    """Manage archived environment variable keys."""


@archival_group.command("mark")
@click.argument("key")
@click.option("--reason", default="", help="Optional reason for archiving.")
@click.pass_context
def mark_archived(ctx: click.Context, key: str, reason: str) -> None:
    """Mark KEY as archived."""
    mgr = _get_manager(ctx)
    try:
        mgr.archive(key, reason or None)
        click.echo(f"Key '{key}' has been archived.")
    except ArchivalError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@archival_group.command("unmark")
@click.argument("key")
@click.pass_context
def unmark_archived(ctx: click.Context, key: str) -> None:
    """Remove KEY from the archived set."""
    mgr = _get_manager(ctx)
    try:
        mgr.unarchive(key)
        click.echo(f"Key '{key}' has been unarchived.")
    except ArchivalError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@archival_group.command("list")
@click.pass_context
def list_archived(ctx: click.Context) -> None:
    """List all archived keys."""
    mgr = _get_manager(ctx)
    keys = mgr.list_archived()
    if not keys:
        click.echo("No archived keys.")
        return
    for key in keys:
        info = mgr.get_info(key)
        reason = f" — {info['reason']}" if info and info.get("reason") else ""
        archived_at = info.get("archived_at", "") if info else ""
        click.echo(f"{key}  (archived: {archived_at}{reason})")


@archival_group.command("check")
@click.argument("key")
@click.pass_context
def check_archived(ctx: click.Context, key: str) -> None:
    """Check whether KEY is archived."""
    mgr = _get_manager(ctx)
    if mgr.is_archived(key):
        info = mgr.get_info(key)
        click.echo(f"'{key}' is archived (since {info['archived_at']}).")
    else:
        click.echo(f"'{key}' is not archived.")
