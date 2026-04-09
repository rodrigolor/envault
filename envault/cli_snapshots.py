"""CLI commands for vault snapshot management."""

from pathlib import Path

import click

from envault.cli import get_vault
from envault.snapshots import SnapshotError, SnapshotManager


def _get_manager(ctx: click.Context) -> SnapshotManager:
    vault = get_vault(ctx)
    base_dir = Path(click.get_current_context().obj.get("vault_dir", Path.home() / ".envault"))
    return SnapshotManager(vault, base_dir)


@click.group("snapshot")
def snapshot_group() -> None:
    """Manage vault snapshots."""


@snapshot_group.command("create")
@click.argument("name")
@click.pass_context
def create_snapshot(ctx: click.Context, name: str) -> None:
    """Capture the current vault state as NAME."""
    try:
        mgr = _get_manager(ctx)
        mgr.create(name)
        click.echo(f"Snapshot '{name}' created.")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@snapshot_group.command("restore")
@click.argument("name")
@click.pass_context
def restore_snapshot(ctx: click.Context, name: str) -> None:
    """Restore vault variables from snapshot NAME."""
    try:
        mgr = _get_manager(ctx)
        count = mgr.restore(name)
        click.echo(f"Restored {count} variable(s) from snapshot '{name}'.")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@snapshot_group.command("delete")
@click.argument("name")
@click.pass_context
def delete_snapshot(ctx: click.Context, name: str) -> None:
    """Delete snapshot NAME."""
    try:
        mgr = _get_manager(ctx)
        mgr.delete(name)
        click.echo(f"Snapshot '{name}' deleted.")
    except SnapshotError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@snapshot_group.command("list")
@click.pass_context
def list_snapshots(ctx: click.Context) -> None:
    """List all available snapshots."""
    mgr = _get_manager(ctx)
    snapshots = mgr.list_snapshots()
    if not snapshots:
        click.echo("No snapshots found.")
        return
    for snap in snapshots:
        click.echo(f"  {snap['name']:20s}  {snap['created_at']}  ({snap['count']} keys)")
