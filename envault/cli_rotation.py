"""CLI commands for key rotation in envault."""

from __future__ import annotations

from pathlib import Path

import click

from envault.rotation import KeyRotationManager, RotationError


@click.group(name="rotate")
def rotation_group():
    """Key rotation commands."""


@rotation_group.command("run")
@click.option("--vault-path", default=".envault", show_default=True,
              help="Path to the vault directory.")
@click.option("--old-password", prompt=True, hide_input=True,
              help="Current vault password.")
@click.option("--new-password", prompt=True, hide_input=True,
              confirmation_prompt=True, help="New vault password.")
def run_rotation(vault_path: str, old_password: str, new_password: str):
    """Re-encrypt the vault with a new password."""
    manager = KeyRotationManager(Path(vault_path))
    try:
        count = manager.rotate(old_password, new_password)
        click.echo(f"\u2713 Key rotation complete. {count} variable(s) re-encrypted.")
    except RotationError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@rotation_group.command("check")
@click.option("--vault-path", default=".envault", show_default=True,
              help="Path to the vault directory.")
@click.option("--max-age", default=90, show_default=True,
              help="Maximum key age in days before rotation is recommended.")
def check_rotation(vault_path: str, max_age: int):
    """Check whether key rotation is recommended."""
    manager = KeyRotationManager(Path(vault_path))
    if manager.needs_rotation("", max_age_days=max_age):
        click.echo(
            f"\u26a0 Key rotation is recommended (threshold: {max_age} days)."
        )
    else:
        click.echo("\u2713 Key is within the acceptable age range.")
