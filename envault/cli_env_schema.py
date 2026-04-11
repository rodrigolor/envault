"""CLI commands for managing env variable schemas."""
from __future__ import annotations

from pathlib import Path

import click

from envault.env_schema import EnvSchema, SchemaError
from envault.vault import Vault
from envault.cli import get_vault


def _get_schema(base_dir: str | None = None) -> EnvSchema:
    root = Path(base_dir) if base_dir else Path.home() / ".envault"
    return EnvSchema(root / "schema.json")


@click.group(name="schema")
def schema_group() -> None:
    """Manage the environment variable schema."""


@schema_group.command("define")
@click.argument("key")
@click.option("--type", "var_type", default="string", show_default=True,
              type=click.Choice(["string", "integer", "float", "boolean"]),
              help="Expected type for this variable.")
@click.option("--optional", is_flag=True, default=False, help="Mark key as optional.")
@click.option("--description", default="", help="Human-readable description.")
@click.option("--base-dir", default=None, hidden=True)
def define_key(key: str, var_type: str, optional: bool, description: str, base_dir: str | None) -> None:
    """Define a key in the schema."""
    schema = _get_schema(base_dir)
    try:
        schema.define(key, type=var_type, required=not optional, description=description)
        click.echo(f"Defined '{key}' as {var_type} ({'optional' if optional else 'required'}).")
    except SchemaError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@schema_group.command("remove")
@click.argument("key")
@click.option("--base-dir", default=None, hidden=True)
def remove_key(key: str, base_dir: str | None) -> None:
    """Remove a key from the schema."""
    schema = _get_schema(base_dir)
    try:
        schema.remove(key)
        click.echo(f"Removed '{key}' from schema.")
    except SchemaError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@schema_group.command("list")
@click.option("--base-dir", default=None, hidden=True)
def list_schema(base_dir: str | None) -> None:
    """List all keys defined in the schema."""
    schema = _get_schema(base_dir)
    keys = schema.list_keys()
    if not keys:
        click.echo("No keys defined in schema.")
        return
    for key, rules in keys.items():
        req = "required" if rules.get("required", True) else "optional"
        desc = f" — {rules['description']}" if rules.get("description") else ""
        click.echo(f"  {key} [{rules['type']}, {req}]{desc}")


@schema_group.command("validate")
@click.option("--base-dir", default=None, hidden=True)
@click.pass_context
def validate_vault(ctx: click.Context, base_dir: str | None) -> None:
    """Validate the current vault contents against the schema."""
    schema = _get_schema(base_dir)
    vault: Vault = ctx.obj["vault"] if ctx.obj else get_vault()
    env = vault.get_all()
    errors = schema.validate(env)
    if not errors:
        click.echo("Validation passed. All required keys are present and correctly typed.")
    else:
        for err in errors:
            click.echo(f"  ✗ {err}", err=True)
        raise SystemExit(1)
