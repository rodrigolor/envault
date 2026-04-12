"""CLI commands for secret detection and masking."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.env_secrets import SecretManager


@click.group(name="secrets")
def secrets_group():
    """Detect and manage sensitive environment variables."""


@secrets_group.command(name="scan")
@click.option("--profile", default="default", show_default=True, help="Vault profile to scan.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def scan_secrets(profile: str, password: str):
    """Scan vault for potentially sensitive variables."""
    vault = get_vault(profile, password)
    manager = SecretManager()
    env = vault.get_all()

    if not env:
        click.echo("Vault is empty.")
        return

    result = manager.scan(env)
    click.echo(result.summary())
    if result.has_secrets:
        raise SystemExit(1)


@secrets_group.command(name="show")
@click.option("--profile", default="default", show_default=True, help="Vault profile.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--unmask", is_flag=True, default=False, help="Show real values (dangerous).")
def show_secrets(profile: str, password: str, unmask: bool):
    """List all variables, masking sensitive values by default."""
    vault = get_vault(profile, password)
    manager = SecretManager()
    env = vault.get_all()

    if not env:
        click.echo("Vault is empty.")
        return

    display = env if unmask else manager.mask_all(env)
    for key, value in sorted(display.items()):
        click.echo(f"{key}={value}")


@secrets_group.command(name="check")
@click.argument("key")
@click.option("--profile", default="default", show_default=True, help="Vault profile.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
def check_key(key: str, profile: str, password: str):
    """Check whether a specific key is considered sensitive."""
    vault = get_vault(profile, password)
    manager = SecretManager()
    value = vault.get(key)

    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)

    key_sensitive = manager.is_sensitive_key(key)
    val_sensitive = manager.is_sensitive_value(value)

    if key_sensitive:
        click.echo(f"'{key}' is flagged: sensitive key name.")
    elif val_sensitive:
        click.echo(f"'{key}' is flagged: sensitive value pattern.")
    else:
        click.echo(f"'{key}' does not appear sensitive.")
