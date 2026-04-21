"""CLI commands for managing env variable checksums."""

import click
from envault.env_checksum import ChecksumManager, ChecksumError
from envault.cli import get_vault


def _get_manager(ctx: click.Context) -> ChecksumManager:
    vault = get_vault(ctx)
    return ChecksumManager(vault.vault_dir)


@click.group(name="checksum")
def checksum_group():
    """Manage checksums for vault keys."""


@checksum_group.command("record")
@click.argument("key")
@click.pass_context
def record_checksum(ctx, key):
    """Record a checksum for a vault key's current value."""
    vault = get_vault(ctx)
    manager = ChecksumManager(vault.vault_dir)
    value = vault.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    digest = manager.record(key, value)
    click.echo(f"Checksum recorded for '{key}': {digest[:16]}...")


@checksum_group.command("verify")
@click.argument("key")
@click.pass_context
def verify_checksum(ctx, key):
    """Verify a vault key's current value matches its recorded checksum."""
    vault = get_vault(ctx)
    manager = ChecksumManager(vault.vault_dir)
    value = vault.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found in vault.", err=True)
        raise SystemExit(1)
    try:
        ok = manager.verify(key, value)
    except ChecksumError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    if ok:
        click.echo(f"OK: '{key}' matches its recorded checksum.")
    else:
        click.echo(f"MISMATCH: '{key}' does not match its recorded checksum!", err=True)
        raise SystemExit(2)


@checksum_group.command("list")
@click.pass_context
def list_checksums(ctx):
    """List all keys with recorded checksums."""
    vault = get_vault(ctx)
    manager = ChecksumManager(vault.vault_dir)
    data = manager.list_all()
    if not data:
        click.echo("No checksums recorded.")
        return
    for key, digest in sorted(data.items()):
        click.echo(f"  {key}: {digest[:16]}...")


@checksum_group.command("remove")
@click.argument("key")
@click.pass_context
def remove_checksum(ctx, key):
    """Remove the recorded checksum for a key."""
    vault = get_vault(ctx)
    manager = ChecksumManager(vault.vault_dir)
    try:
        manager.remove(key)
        click.echo(f"Checksum for '{key}' removed.")
    except ChecksumError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
