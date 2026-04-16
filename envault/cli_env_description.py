"""CLI commands for managing environment variable descriptions."""

import click
from envault.env_description import DescriptionManager, DescriptionError
from envault.cli import get_vault


def _get_manager(vault_dir: str) -> DescriptionManager:
    return DescriptionManager(vault_dir)


@click.group("describe")
def description_group():
    """Manage descriptions for environment variables."""


@description_group.command("set")
@click.argument("key")
@click.argument("description")
@click.option("--vault-dir", default=".envault", show_default=True)
def set_description(key, description, vault_dir):
    """Set a description for a key."""
    mgr = _get_manager(vault_dir)
    try:
        mgr.set(key, description)
        click.echo(f"Description set for '{key}'.")
    except DescriptionError as e:
        click.echo(f"Error: {e}", err=True)


@description_group.command("get")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
def get_description(key, vault_dir):
    """Get the description for a key."""
    mgr = _get_manager(vault_dir)
    desc = mgr.get(key)
    if desc is None:
        click.echo(f"No description for '{key}'.")
    else:
        click.echo(f"{key}: {desc}")


@description_group.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
def remove_description(key, vault_dir):
    """Remove the description for a key."""
    mgr = _get_manager(vault_dir)
    try:
        mgr.remove(key)
        click.echo(f"Description removed for '{key}'.")
    except DescriptionError as e:
        click.echo(f"Error: {e}", err=True)


@description_group.command("list")
@click.option("--vault-dir", default=".envault", show_default=True)
def list_descriptions(vault_dir):
    """List all key descriptions."""
    mgr = _get_manager(vault_dir)
    entries = mgr.list_all()
    if not entries:
        click.echo("No descriptions defined.")
    else:
        for key, desc in entries.items():
            click.echo(f"  {key}: {desc}")
