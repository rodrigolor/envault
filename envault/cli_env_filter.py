"""CLI commands for filtering environment variables."""

import click
from envault.cli import get_vault
from envault.env_filter import EnvFilter, FilterError


@click.group("filter")
def filter_group():
    """Filter vault variables by various criteria."""


def _print_vars(data: dict):
    if not data:
        click.echo("No matching variables.")
        return
    for k, v in sorted(data.items()):
        click.echo(f"{k}={v}")


@filter_group.command("prefix")
@click.argument("prefix")
@click.pass_context
def by_prefix(ctx, prefix):
    """Show variables whose keys start with PREFIX."""
    vault = get_vault(ctx)
    f = EnvFilter(vault)
    _print_vars(f.by_prefix(prefix))


@filter_group.command("suffix")
@click.argument("suffix")
@click.pass_context
def by_suffix(ctx, suffix):
    """Show variables whose keys end with SUFFIX."""
    vault = get_vault(ctx)
    f = EnvFilter(vault)
    _print_vars(f.by_suffix(suffix))


@filter_group.command("pattern")
@click.argument("pattern")
@click.pass_context
def by_pattern(ctx, pattern):
    """Show variables matching a glob PATTERN."""
    vault = get_vault(ctx)
    f = EnvFilter(vault)
    _print_vars(f.by_pattern(pattern))


@filter_group.command("type")
@click.argument("value_type", metavar="TYPE", type=click.Choice(["bool", "int", "float", "str"]))
@click.pass_context
def by_type(ctx, value_type):
    """Show variables whose values match TYPE (bool, int, float, str)."""
    vault = get_vault(ctx)
    f = EnvFilter(vault)
    try:
        _print_vars(f.by_value_type(value_type))
    except FilterError as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(1)


@filter_group.command("exclude")
@click.argument("keys", nargs=-1, required=True)
@click.pass_context
def exclude(ctx, keys):
    """Show all variables except the specified KEYS."""
    vault = get_vault(ctx)
    f = EnvFilter(vault)
    _print_vars(f.exclude_keys(list(keys)))


@filter_group.command("only")
@click.argument("keys", nargs=-1, required=True)
@click.pass_context
def only(ctx, keys):
    """Show only the specified KEYS."""
    vault = get_vault(ctx)
    f = EnvFilter(vault)
    _print_vars(f.only_keys(list(keys)))
