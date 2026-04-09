"""CLI entry point for envault using Click."""

import sys
import click
from envault.vault import Vault
from envault.storage import LocalStorage


def get_vault(path: str, password: str) -> Vault:
    """Helper to create a Vault instance from CLI options."""
    storage = LocalStorage(path)
    return Vault(storage=storage, password=password)


@click.group()
@click.version_option(version="0.1.0", prog_name="envault")
def cli():
    """envault — securely store and sync environment variables."""
    pass


@cli.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--path", default=".envault", show_default=True, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def set_var(key: str, value: str, path: str, password: str):
    """Set an environment variable in the vault."""
    try:
        vault = get_vault(path, password)
        vault.set(key, value)
        click.echo(f"✔ Set '{key}' successfully.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("get")
@click.argument("key")
@click.option("--path", default=".envault", show_default=True, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def get_var(key: str, path: str, password: str):
    """Get an environment variable from the vault."""
    try:
        vault = get_vault(path, password)
        value = vault.get(key)
        if value is None:
            click.echo(f"Key '{key}' not found.", err=True)
            sys.exit(1)
        click.echo(value)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("list")
@click.option("--path", default=".envault", show_default=True, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def list_vars(path: str, password: str):
    """List all keys stored in the vault."""
    try:
        vault = get_vault(path, password)
        variables = vault.get_all()
        if not variables:
            click.echo("Vault is empty.")
            return
        for key, value in variables.items():
            click.echo(f"{key}={value}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command("delete")
@click.argument("key")
@click.option("--path", default=".envault", show_default=True, help="Vault file path.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def delete_var(key: str, path: str, password: str):
    """Delete an environment variable from the vault."""
    try:
        vault = get_vault(path, password)
        removed = vault.delete(key)
        if not removed:
            click.echo(f"Key '{key}' not found.", err=True)
            sys.exit(1)
        click.echo(f"✔ Deleted '{key}' successfully.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
