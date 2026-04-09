"""CLI commands for tagging vault variables."""

import click
from envault.cli import get_vault
from envault.tags import TagManager, TagError


@click.group(name="tag")
def tag_group():
    """Manage tags for vault variables."""


def _get_manager(ctx) -> TagManager:
    vault = get_vault(ctx)
    return TagManager(vault)


@tag_group.command("add")
@click.argument("key")
@click.argument("tag")
@click.pass_context
def add_tag(ctx, key: str, tag: str):
    """Add TAG to KEY."""
    try:
        mgr = _get_manager(ctx)
        mgr.tag(key, tag)
        click.echo(f"Tagged '{key}' with '{tag}'.")
    except TagError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@tag_group.command("remove")
@click.argument("key")
@click.argument("tag")
@click.pass_context
def remove_tag(ctx, key: str, tag: str):
    """Remove TAG from KEY."""
    try:
        mgr = _get_manager(ctx)
        mgr.untag(key, tag)
        click.echo(f"Removed tag '{tag}' from '{key}'.")
    except TagError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@tag_group.command("list")
@click.argument("key")
@click.pass_context
def list_tags(ctx, key: str):
    """List all tags on KEY."""
    mgr = _get_manager(ctx)
    tags = mgr.get_tags(key)
    if tags:
        for t in tags:
            click.echo(t)
    else:
        click.echo(f"No tags found for '{key}'.")


@tag_group.command("find")
@click.argument("tag")
@click.pass_context
def find_by_tag(ctx, tag: str):
    """Find all keys with TAG."""
    mgr = _get_manager(ctx)
    keys = mgr.find_by_tag(tag)
    if keys:
        for k in keys:
            click.echo(k)
    else:
        click.echo(f"No keys found with tag '{tag}'.")


@tag_group.command("all")
@click.pass_context
def all_tags(ctx):
    """List every tag currently in use."""
    mgr = _get_manager(ctx)
    tags = mgr.list_all_tags()
    if tags:
        for t in tags:
            click.echo(t)
    else:
        click.echo("No tags defined.")
