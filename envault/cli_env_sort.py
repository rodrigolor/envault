"""CLI commands for sorting and grouping environment variables."""

import click

from envault.cli import get_vault
from envault.env_sort import EnvSorter, SortError


@click.group("sort")
def sort_group() -> None:
    """Sort and group environment variable keys."""


@sort_group.command("list")
@click.option(
    "--mode",
    default="alpha",
    show_default=True,
    type=click.Choice(["alpha", "alpha_desc", "length", "length_desc"]),
    help="Sort mode.",
)
@click.pass_context
def list_sorted(ctx: click.Context, mode: str) -> None:
    """List all variables in sorted order."""
    vault = get_vault(ctx)
    sorter = EnvSorter(vault)
    try:
        items = sorter.sort(mode)
    except SortError as exc:
        raise click.ClickException(str(exc)) from exc

    if not items:
        click.echo("No variables stored.")
        return

    for key, value in items.items():
        click.echo(f"{key}={value}")


@sort_group.command("group")
@click.option(
    "--separator",
    default="_",
    show_default=True,
    help="Prefix separator character.",
)
@click.pass_context
def group_by_prefix(ctx: click.Context, separator: str) -> None:
    """Group variables by their key prefix."""
    vault = get_vault(ctx)
    sorter = EnvSorter(vault)
    groups = sorter.group_by_prefix(separator)

    if not groups:
        click.echo("No variables stored.")
        return

    for prefix, members in groups.items():
        click.echo(f"[{prefix}]")
        for key, value in members.items():
            click.echo(f"  {key}={value}")
