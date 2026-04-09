"""CLI commands for exporting and importing vault variables."""

import sys
from pathlib import Path

import click

from envault.cli import get_vault
from envault.export import ExportManager, SUPPORTED_FORMATS


@click.group("export")
def export_group():
    """Export or import environment variables."""


@export_group.command("dump")
@click.option("--profile", default="default", show_default=True, help="Vault profile to use.")
@click.option(
    "--format", "fmt",
    type=click.Choice(SUPPORTED_FORMATS),
    default="dotenv",
    show_default=True,
    help="Output format.",
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Write to file instead of stdout.")
@click.pass_context
def dump(ctx, profile, fmt, output):
    """Dump all vault variables to a file or stdout."""
    vault = get_vault(profile)
    variables = vault.get_all()
    if not variables:
        click.echo("No variables stored in vault.", err=True)
        return

    manager = ExportManager()
    content = manager.export(variables, fmt=fmt)

    if output:
        Path(output).write_text(content)
        click.echo(f"Exported {len(variables)} variable(s) to '{output}' [{fmt}].")
    else:
        click.echo(content, nl=False)


@export_group.command("load")
@click.argument("file", type=click.Path(exists=True))
@click.option("--profile", default="default", show_default=True, help="Vault profile to use.")
@click.option(
    "--format", "fmt",
    type=click.Choice(SUPPORTED_FORMATS),
    default="dotenv",
    show_default=True,
    help="Input format.",
)
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.pass_context
def load_file(ctx, file, profile, fmt, overwrite):
    """Load variables from a file into the vault."""
    vault = get_vault(profile)
    manager = ExportManager()

    content = Path(file).read_text()
    try:
        variables = manager.import_data(content, fmt=fmt)
    except (ValueError, Exception) as exc:
        click.echo(f"Error parsing file: {exc}", err=True)
        sys.exit(1)

    imported = 0
    skipped = 0
    for key, value in variables.items():
        if not overwrite and vault.get(key) is not None:
            skipped += 1
            continue
        vault.set(key, value)
        imported += 1

    click.echo(f"Imported {imported} variable(s) from '{file}' [{fmt}]."
               + (f" Skipped {skipped} existing key(s)." if skipped else ""))
