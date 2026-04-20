"""CLI commands for managing required environment variables."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_required import RequiredError, RequiredManager


def _get_manager(ctx: click.Context) -> RequiredManager:
    base_dir = ctx.obj.get("base_dir", ".envault")
    return RequiredManager(base_dir)


@click.group("required")
def required_group() -> None:
    """Manage required environment variable declarations."""


@required_group.command("mark")
@click.argument("key")
@click.pass_context
def mark_required(ctx: click.Context, key: str) -> None:
    """Mark KEY as required."""
    mgr = _get_manager(ctx)
    try:
        mgr.mark_required(key)
        click.echo(f"Key '{key}' marked as required.")
    except RequiredError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@required_group.command("unmark")
@click.argument("key")
@click.pass_context
def unmark_required(ctx: click.Context, key: str) -> None:
    """Remove the required mark from KEY."""
    mgr = _get_manager(ctx)
    try:
        mgr.unmark_required(key)
        click.echo(f"Key '{key}' is no longer required.")
    except RequiredError as exc:
        click.echo(f"Error: {exc}", err=True)
        ctx.exit(1)


@required_group.command("list")
@click.pass_context
def list_required(ctx: click.Context) -> None:
    """List all required keys."""
    mgr = _get_manager(ctx)
    keys = mgr.list_required()
    if not keys:
        click.echo("No required keys defined.")
    else:
        for k in keys:
            click.echo(k)


@required_group.command("check")
@click.pass_context
def check_required(ctx: click.Context) -> None:
    """Check that all required keys are present in the vault."""
    from envault.cli import get_vault  # local import to avoid circular deps

    mgr = _get_manager(ctx)
    vault = get_vault(ctx)
    missing = mgr.validate(list(vault.get_all().keys()))
    if missing:
        click.echo("Missing required keys:", err=True)
        for k in missing:
            click.echo(f"  - {k}", err=True)
        ctx.exit(1)
    else:
        click.echo("All required keys are present.")
