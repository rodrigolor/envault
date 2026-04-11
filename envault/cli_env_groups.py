"""CLI commands for environment variable group management."""

import click
from envault.env_groups import GroupManager, GroupError


def _get_manager(ctx: click.Context) -> GroupManager:
    base_dir = ctx.obj.get("base_dir", ".envault")
    return GroupManager(base_dir)


@click.group(name="group")
def group_cmd():
    """Manage groups of environment variable keys."""


@group_cmd.command("create")
@click.argument("name")
@click.pass_context
def create_group(ctx: click.Context, name: str):
    """Create a new empty group."""
    mgr = _get_manager(ctx)
    try:
        mgr.create(name)
        click.echo(f"Group '{name}' created.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("delete")
@click.argument("name")
@click.pass_context
def delete_group(ctx: click.Context, name: str):
    """Delete an existing group."""
    mgr = _get_manager(ctx)
    try:
        mgr.delete(name)
        click.echo(f"Group '{name}' deleted.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("add")
@click.argument("group")
@click.argument("key")
@click.pass_context
def add_key(ctx: click.Context, group: str, key: str):
    """Add a key to a group."""
    mgr = _get_manager(ctx)
    try:
        mgr.add_key(group, key)
        click.echo(f"Key '{key}' added to group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("remove")
@click.argument("group")
@click.argument("key")
@click.pass_context
def remove_key(ctx: click.Context, group: str, key: str):
    """Remove a key from a group."""
    mgr = _get_manager(ctx)
    try:
        mgr.remove_key(group, key)
        click.echo(f"Key '{key}' removed from group '{group}'.")
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@group_cmd.command("list")
@click.pass_context
def list_groups(ctx: click.Context):
    """List all groups."""
    mgr = _get_manager(ctx)
    groups = mgr.list_groups()
    if not groups:
        click.echo("No groups defined.")
    else:
        for g in groups:
            keys = mgr.get_keys(g)
            click.echo(f"{g}: {', '.join(keys) if keys else '(empty)'}")


@group_cmd.command("show")
@click.argument("name")
@click.pass_context
def show_group(ctx: click.Context, name: str):
    """Show all keys in a group."""
    mgr = _get_manager(ctx)
    try:
        keys = mgr.get_keys(name)
        if not keys:
            click.echo(f"Group '{name}' is empty.")
        else:
            for k in keys:
                click.echo(k)
    except GroupError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
