"""CLI commands for renaming vault keys."""

import click
from envault.cli import get_vault
from envault.env_rename import RenameManager, RenameError


@click.group("rename")
def rename_group():
    """Rename environment variable keys in the vault."""
    pass


@rename_group.command("key")
@click.argument("old_key")
@click.argument("new_key")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite target key if it exists.")
@click.option("--preview", is_flag=True, default=False, help="Preview the rename without applying it.")
@click.pass_context
def rename_key(ctx, old_key, new_key, overwrite, preview):
    """Rename OLD_KEY to NEW_KEY in the vault."""
    vault = get_vault(ctx)
    manager = RenameManager(vault)

    if preview:
        result = manager.preview_rename(old_key, new_key)
        click.echo(f"Preview: '{result['old_key']}' -> '{result['new_key']}'")
        click.echo(f"  Value : {result['value']}")
        click.echo(f"  Target exists: {result['target_exists']}")
        if result["issues"]:
            for issue in result["issues"]:
                click.echo(f"  ⚠ {issue}", err=True)
        else:
            click.echo("  ✓ Safe to rename.")
        return

    try:
        manager.rename(old_key, new_key, overwrite=overwrite)
        click.echo(f"Renamed '{old_key}' to '{new_key}'.")
    except RenameError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@rename_group.command("bulk")
@click.argument("pairs", nargs=-1, required=True, metavar="OLD=NEW...")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite target keys if they exist.")
@click.pass_context
def bulk_rename(ctx, pairs, overwrite):
    """Rename multiple keys at once using OLD=NEW pairs."""
    vault = get_vault(ctx)
    manager = RenameManager(vault)

    mapping = {}
    for pair in pairs:
        if "=" not in pair:
            click.echo(f"Invalid pair '{pair}': expected OLD=NEW format.", err=True)
            ctx.exit(1)
            return
        old, new = pair.split("=", 1)
        mapping[old] = new

    try:
        results = manager.bulk_rename(mapping, overwrite=overwrite)
        for old, new in results.items():
            click.echo(f"Renamed '{old}' -> '{new}'")
    except RenameError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)
