"""CLI commands for vault sharing."""

import click
from envault.cli import get_vault
from envault.sharing import SharingManager, SharingError


@click.group(name="share")
def share_group():
    """Share encrypted vault variables with others."""


@share_group.command("create")
@click.argument("keys", nargs=-1, required=True)
@click.option("--out", required=True, help="Output path for the share bundle (.json)")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True,
              help="Password to encrypt the share bundle.")
@click.option("--vault-password", envvar="ENVAULT_PASSWORD", prompt=True,
              hide_input=True, help="Vault password.")
def create_share(keys, out, password, vault_password):
    """Create an encrypted share bundle for the given KEYS."""
    try:
        vault = get_vault(vault_password)
        mgr = SharingManager(vault)
        bundle = mgr.create_share(list(keys), password)
        mgr.save_share(bundle, out)
        click.echo(f"Share bundle written to {out} ({len(keys)} key(s)).")
    except SharingError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@share_group.command("apply")
@click.argument("bundle_file")
@click.option("--password", prompt=True, hide_input=True,
              help="Password used to encrypt the share bundle.")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing keys in the vault.")
@click.option("--vault-password", envvar="ENVAULT_PASSWORD", prompt=True,
              hide_input=True, help="Vault password.")
def apply_share(bundle_file, password, overwrite, vault_password):
    """Import variables from an encrypted share bundle."""
    try:
        vault = get_vault(vault_password)
        mgr = SharingManager(vault)
        bundle = mgr.load_share(bundle_file)
        imported = mgr.apply_share(bundle, password, overwrite=overwrite)
        if imported:
            click.echo(f"Imported {len(imported)} key(s): {', '.join(imported)}")
        else:
            click.echo("No new keys imported (use --overwrite to replace existing keys).")
    except SharingError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
