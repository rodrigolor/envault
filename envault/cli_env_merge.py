"""CLI commands for merging env sources into the active vault."""

from pathlib import Path

import click

from envault.cli import get_vault
from envault.env_merge import EnvMerger, MergeError


@click.group("merge")
def merge_group():
    """Merge environment variables from external sources."""


@merge_group.command("file")
@click.argument("filepath", type=click.Path(exists=True, path_type=Path))
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview changes without applying.")
@click.pass_context
def merge_file(ctx: click.Context, filepath: Path, overwrite: bool, dry_run: bool):
    """Merge variables from a .env FILE into the vault."""
    vault = get_vault(ctx)
    merger = EnvMerger(vault)

    try:
        if dry_run:
            # Parse without writing
            from envault.env_merge import EnvMerger as _M

            class _NoOpVault:
                def __init__(self, real):
                    self._real = real
                    self._written: dict = {}

                def get(self, key):
                    return self._real.get(key)

                def set(self, key, value):
                    self._written[key] = value

            noop = _NoOpVault(vault)
            result = _M(noop).merge_file(filepath, overwrite=overwrite)
            click.echo(f"[dry-run] {result.summary()}")
            for k in result.added:
                click.echo(f"  + {k}")
            for k in result.updated:
                click.echo(f"  ~ {k}")
            for k in result.skipped:
                click.echo(f"  = {k} (skipped)")
        else:
            result = merger.merge_file(filepath, overwrite=overwrite)
            click.echo(result.summary())
            for k in result.added:
                click.echo(f"  + {k}")
            for k in result.updated:
                click.echo(f"  ~ {k}")
    except MergeError as exc:
        raise click.ClickException(str(exc)) from exc
