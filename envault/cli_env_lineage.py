"""CLI commands for managing key lineage."""

from __future__ import annotations

import click

from envault.env_lineage import LineageError, LineageManager


def _get_manager(ctx: click.Context) -> LineageManager:
    base_dir = ctx.obj.get("base_dir", ".envault")
    return LineageManager(base_dir)


@click.group("lineage")
def lineage_group() -> None:
    """Track and inspect key lineage / origin metadata."""


@lineage_group.command("record")
@click.argument("key")
@click.argument("origin")
@click.option("--derived-from", default=None, help="Parent key this was derived from.")
@click.pass_context
def record_lineage(ctx: click.Context, key: str, origin: str, derived_from: str) -> None:
    """Record the origin of KEY."""
    mgr = _get_manager(ctx)
    try:
        mgr.record(key, origin, derived_from)
        click.echo(f"Recorded lineage for '{key}': origin='{origin}'.")
    except LineageError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lineage_group.command("show")
@click.argument("key")
@click.pass_context
def show_lineage(ctx: click.Context, key: str) -> None:
    """Show lineage info for KEY."""
    mgr = _get_manager(ctx)
    info = mgr.get(key)
    if info is None:
        click.echo(f"No lineage record found for '{key}'.")
    else:
        click.echo(f"Key       : {key}")
        click.echo(f"Origin    : {info['origin']}")
        click.echo(f"Derived from: {info.get('derived_from') or '—'}")


@lineage_group.command("children")
@click.argument("parent_key")
@click.pass_context
def list_children(ctx: click.Context, parent_key: str) -> None:
    """List all keys derived from PARENT_KEY."""
    mgr = _get_manager(ctx)
    children = mgr.derived_from(parent_key)
    if not children:
        click.echo(f"No keys derived from '{parent_key}'.")
    else:
        for child in children:
            click.echo(child)


@lineage_group.command("remove")
@click.argument("key")
@click.pass_context
def remove_lineage(ctx: click.Context, key: str) -> None:
    """Remove lineage record for KEY."""
    mgr = _get_manager(ctx)
    try:
        mgr.remove(key)
        click.echo(f"Removed lineage record for '{key}'.")
    except LineageError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@lineage_group.command("list")
@click.pass_context
def list_all(ctx: click.Context) -> None:
    """List all recorded lineage entries."""
    mgr = _get_manager(ctx)
    data = mgr.list_all()
    if not data:
        click.echo("No lineage records found.")
    else:
        for key, info in data.items():
            derived = info.get("derived_from") or "—"
            click.echo(f"{key}  origin={info['origin']}  derived_from={derived}")
