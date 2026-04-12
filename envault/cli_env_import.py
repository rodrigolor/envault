"""CLI commands for importing environment variables from external files."""

import click
from envault.cli import get_vault
from envault.env_import import EnvImporter, ImportError as EnvImportError


@click.group(name="import")
def import_group():
    """Import environment variables from external files."""


@import_group.command(name="file")
@click.argument("path")
@click.option("--format", "fmt", type=click.Choice(["dotenv", "json", "shell"]), default=None,
              help="File format (auto-detected if omitted).")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing keys.")
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option("--profile", default="default", help="Vault profile.")
def import_file(path, fmt, overwrite, password, profile):
    """Import variables from PATH into the vault."""
    try:
        vault = get_vault(profile, password)
        importer = EnvImporter(vault)
        imported = importer.import_file(path, fmt=fmt, overwrite=overwrite)
        if imported:
            click.echo(f"Imported {len(imported)} variable(s):")
            for key in imported:
                click.echo(f"  {key}")
        else:
            click.echo("No new variables imported (use --overwrite to replace existing keys).")
    except EnvImportError as e:
        click.echo(f"Import error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise SystemExit(1)


@import_group.command(name="preview")
@click.argument("path")
@click.option("--format", "fmt", type=click.Choice(["dotenv", "json", "shell"]), default=None,
              help="File format (auto-detected if omitted).")
def preview(path, fmt):
    """Preview variables that would be imported from PATH without saving."""
    from pathlib import Path

    class _NoOpVault:
        def get(self, key):
            return None
        def set(self, key, value):
            pass

    try:
        importer = EnvImporter(_NoOpVault())
        imported = importer.import_file(path, fmt=fmt, overwrite=True)
        if imported:
            click.echo(f"Would import {len(imported)} variable(s):")
            for key, value in imported.items():
                click.echo(f"  {key}={value}")
        else:
            click.echo("No variables found in file.")
    except EnvImportError as e:
        click.echo(f"Import error: {e}", err=True)
        raise SystemExit(1)
