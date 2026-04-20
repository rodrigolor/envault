"""CLI commands for environment variable ownership management."""

import click
from envault.env_ownership import OwnershipManager, OwnershipError


def _get_manager(ctx: click.Context) -> OwnershipManager:
    base_dir = ctx.obj.get("base_dir", ".envault")
    return OwnershipManager(base_dir)


@click.group(name="ownership")
def ownership_group():
    """Manage ownership of environment variable keys."""


@ownership_group.command("assign")
@click.argument("key")
@click.argument("owner")
@click.pass_context
def assign_owner(ctx, key, owner):
    """Assign OWNER to KEY."""
    mgr = _get_manager(ctx)
    try:
        mgr.assign(key, owner)
        click.echo(f"Assigned '{owner}' as owner of '{key}'.")
    except OwnershipError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ownership_group.command("unassign")
@click.argument("key")
@click.pass_context
def unassign_owner(ctx, key):
    """Remove ownership record for KEY."""
    mgr = _get_manager(ctx)
    try:
        mgr.unassign(key)
        click.echo(f"Ownership record for '{key}' removed.")
    except OwnershipError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@ownership_group.command("get")
@click.argument("key")
@click.pass_context
def get_owner(ctx, key):
    """Show the owner of KEY."""
    mgr = _get_manager(ctx)
    owner = mgr.get_owner(key)
    if owner:
        click.echo(f"{key}: {owner}")
    else:
        click.echo(f"'{key}' has no owner.")


@ownership_group.command("list")
@click.pass_context
def list_owners(ctx):
    """List all owned keys."""
    mgr = _get_manager(ctx)
    owned = mgr.list_owned()
    if not owned:
        click.echo("No ownership records found.")
        return
    for key, owner in sorted(owned.items()):
        click.echo(f"  {key}: {owner}")


@ownership_group.command("transfer")
@click.argument("key")
@click.argument("new_owner")
@click.pass_context
def transfer_owner(ctx, key, new_owner):
    """Transfer ownership of KEY to NEW_OWNER."""
    mgr = _get_manager(ctx)
    try:
        mgr.transfer(key, new_owner)
        click.echo(f"Ownership of '{key}' transferred to '{new_owner}'.")
    except OwnershipError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
