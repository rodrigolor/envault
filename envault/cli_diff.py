"""CLI commands for vault diff operations."""

import json

import click

from envault.cli import get_vault
from envault.diff import DiffError, DiffManager


@click.group("diff")
def diff_group():
    """Compare vault states."""


@diff_group.command("snapshot")
@click.argument("snapshot_file", type=click.Path(exists=True))
@click.option("--password", prompt=True, hide_input=True, help="Vault password.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["text", "json"]),
    default="text",
    show_default=True,
)
def diff_snapshot(snapshot_file: str, password: str, fmt: str):
    """Diff the current vault against a JSON snapshot file."""
    try:
        with open(snapshot_file) as fh:
            other = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise click.ClickException(f"Cannot read snapshot: {exc}")

    vault = get_vault(password)
    manager = DiffManager(vault)

    try:
        result = manager.compare(other)
    except DiffError as exc:
        raise click.ClickException(str(exc))

    if fmt == "json":
        click.echo(
            json.dumps(
                {
                    "added": result.added,
                    "removed": result.removed,
                    "modified": {
                        k: {"old": v[0], "new": v[1]}
                        for k, v in result.modified.items()
                    },
                },
                indent=2,
            )
        )
    else:
        if result.has_changes:
            click.echo(result.summary())
        else:
            click.echo("Vault matches snapshot — no changes.")


@diff_group.command("files")
@click.argument("file_a", type=click.Path(exists=True))
@click.argument("file_b", type=click.Path(exists=True))
def diff_files(file_a: str, file_b: str):
    """Diff two JSON snapshot files against each other."""
    try:
        with open(file_a) as fh:
            snap_a = json.load(fh)
        with open(file_b) as fh:
            snap_b = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise click.ClickException(f"Cannot read file: {exc}")

    manager = DiffManager(vault=None)  # vault not needed for snapshot-to-snapshot
    result = manager.compare_snapshots(snap_a, snap_b)

    if result.has_changes:
        click.echo(result.summary())
    else:
        click.echo("Snapshots are identical — no changes.")
