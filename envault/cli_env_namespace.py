"""CLI commands for namespace management."""

import click
from envault.env_namespace import NamespaceManager, NamespaceError


def _get_manager(ctx) -> NamespaceManager:
    base_dir = ctx.obj.get("base_dir", ".envault")
    return NamespaceManager(base_dir)


@click.group("namespace")
def namespace_group():
    """Manage environment variable namespaces."""


@namespace_group.command("create")
@click.argument("name")
@click.pass_context
def create_namespace(ctx, name):
    """Create a new namespace."""
    mgr = _get_manager(ctx)
    try:
        mgr.create(name)
        click.echo(f"Namespace '{name}' created.")
    except NamespaceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@namespace_group.command("delete")
@click.argument("name")
@click.pass_context
def delete_namespace(ctx, name):
    """Delete a namespace."""
    mgr = _get_manager(ctx)
    try:
        mgr.delete(name)
        click.echo(f"Namespace '{name}' deleted.")
    except NamespaceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@namespace_group.command("assign")
@click.argument("namespace")
@click.argument("key")
@click.pass_context
def assign_key(ctx, namespace, key):
    """Assign a key to a namespace."""
    mgr = _get_manager(ctx)
    try:
        mgr.assign(namespace, key)
        click.echo(f"Key '{key}' assigned to namespace '{namespace}'.")
    except NamespaceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@namespace_group.command("unassign")
@click.argument("namespace")
@click.argument("key")
@click.pass_context
def unassign_key(ctx, namespace, key):
    """Remove a key from a namespace."""
    mgr = _get_manager(ctx)
    try:
        mgr.unassign(namespace, key)
        click.echo(f"Key '{key}' removed from namespace '{namespace}'.")
    except NamespaceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@namespace_group.command("list")
@click.pass_context
def list_namespaces(ctx):
    """List all namespaces."""
    mgr = _get_manager(ctx)
    namespaces = mgr.list_namespaces()
    if not namespaces:
        click.echo("No namespaces defined.")
    else:
        for ns in namespaces:
            click.echo(ns)


@namespace_group.command("keys")
@click.argument("namespace")
@click.pass_context
def list_keys(ctx, namespace):
    """List keys in a namespace."""
    mgr = _get_manager(ctx)
    try:
        keys = mgr.keys_in(namespace)
        if not keys:
            click.echo(f"No keys in namespace '{namespace}'.")
        else:
            for k in keys:
                click.echo(k)
    except NamespaceError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
