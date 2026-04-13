"""CLI commands for placeholder resolution."""

import click
from envault.cli import get_vault
from envault.env_placeholder import PlaceholderResolver, PlaceholderError


@click.group("placeholder")
def placeholder_group():
    """Resolve ${KEY} placeholders in vault values."""


@placeholder_group.command("resolve")
@click.argument("key")
@click.pass_context
def resolve_key(ctx, key: str):
    """Resolve placeholders in the value of KEY."""
    vault = get_vault(ctx)
    value = vault.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    resolver = PlaceholderResolver(vault)
    try:
        resolved = resolver.resolve(value)
        click.echo(f"{key}={resolved}")
    except PlaceholderError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@placeholder_group.command("resolve-all")
@click.pass_context
def resolve_all(ctx):
    """Resolve placeholders for every key in the vault."""
    vault = get_vault(ctx)
    resolver = PlaceholderResolver(vault)
    try:
        resolved = resolver.resolve_all()
        if not resolved:
            click.echo("No variables found.")
            return
        for k, v in sorted(resolved.items()):
            click.echo(f"{k}={v}")
    except PlaceholderError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@placeholder_group.command("list-refs")
@click.argument("key")
@click.pass_context
def list_refs(ctx, key: str):
    """List all placeholder references inside KEY's value."""
    vault = get_vault(ctx)
    value = vault.get(key)
    if value is None:
        click.echo(f"Key '{key}' not found.", err=True)
        raise SystemExit(1)
    resolver = PlaceholderResolver(vault)
    refs = resolver.list_references(value)
    if not refs:
        click.echo(f"No placeholders found in '{key}'.")
    else:
        for ref in refs:
            click.echo(ref)
