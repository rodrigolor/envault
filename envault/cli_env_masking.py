"""CLI commands for managing value masking."""

from __future__ import annotations

from pathlib import Path

import click

from envault.env_masking import MaskingError, MaskingManager
from envault.cli import get_vault


def _get_manager(vault_dir: str) -> MaskingManager:
    return MaskingManager(vault_dir)


@click.group("mask")
def mask_group() -> None:
    """Manage masked (hidden) environment variable values."""


@mask_group.command("add")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
def add_mask(key: str, vault_dir: str) -> None:
    """Mask the value of KEY in all output."""
    mgr = _get_manager(vault_dir)
    try:
        mgr.mask(key)
        click.echo(f"Key '{key}' is now masked.")
    except MaskingError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@mask_group.command("remove")
@click.argument("key")
@click.option("--vault-dir", default=".envault", show_default=True)
def remove_mask(key: str, vault_dir: str) -> None:
    """Remove masking from KEY."""
    mgr = _get_manager(vault_dir)
    try:
        mgr.unmask(key)
        click.echo(f"Key '{key}' is no longer masked.")
    except MaskingError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@mask_group.command("list")
@click.option("--vault-dir", default=".envault", show_default=True)
def list_masked(vault_dir: str) -> None:
    """List all masked keys."""
    mgr = _get_manager(vault_dir)
    keys = mgr.list_masked()
    if not keys:
        click.echo("No keys are currently masked.")
    else:
        for key in keys:
            click.echo(key)


@mask_group.command("show")
@click.option("--vault-dir", default=".envault", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def show_masked(vault_dir: str, password: str) -> None:
    """Display all variables, masking sensitive values."""
    vault = get_vault(vault_dir, password)
    mgr = _get_manager(vault_dir)
    variables = vault.get_all()
    masked = mgr.apply(variables)
    if not masked:
        click.echo("Vault is empty.")
        return
    for key, value in masked.items():
        click.echo(f"{key}={value}")
