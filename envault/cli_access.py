"""CLI commands for managing vault key access control rules."""

import click

from envault.access import AccessManager, AccessError


def _get_manager(ctx: click.Context) -> AccessManager:
    vault_dir = ctx.obj.get("vault_dir", ".envault")
    return AccessManager(vault_dir)


@click.group("access")
def access_group() -> None:
    """Manage read/write access rules for vault keys."""


@access_group.command("set")
@click.argument("pattern")
@click.option("--read/--no-read", default=True, show_default=True, help="Allow read.")
@click.option("--write/--no-write", default=True, show_default=True, help="Allow write.")
@click.pass_context
def set_permissions(ctx: click.Context, pattern: str, read: bool, write: bool) -> None:
    """Set access permissions for a key PATTERN (supports globs)."""
    mgr = _get_manager(ctx)
    perms = []
    if read:
        perms.append("read")
    if write:
        perms.append("write")
    try:
        mgr.set_permissions(pattern, perms)
        click.echo(f"Set permissions for {pattern!r}: {perms}")
    except AccessError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@access_group.command("remove")
@click.argument("pattern")
@click.pass_context
def remove_permissions(ctx: click.Context, pattern: str) -> None:
    """Remove access rules for a key PATTERN."""
    mgr = _get_manager(ctx)
    try:
        mgr.remove_permissions(pattern)
        click.echo(f"Removed rules for pattern {pattern!r}.")
    except AccessError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@access_group.command("check")
@click.argument("key")
@click.pass_context
def check_permissions(ctx: click.Context, key: str) -> None:
    """Show effective permissions for a specific KEY."""
    mgr = _get_manager(ctx)
    perms = mgr.get_permissions(key)
    click.echo(f"Key {key!r} — permissions: {perms}")


@access_group.command("list")
@click.pass_context
def list_rules(ctx: click.Context) -> None:
    """List all defined access rules."""
    mgr = _get_manager(ctx)
    rules = mgr.list_rules()
    if not rules:
        click.echo("No access rules defined.")
        return
    for pattern, perms in rules.items():
        click.echo(f"  {pattern}: {', '.join(perms)}")
