"""CLI commands for template management."""

from __future__ import annotations

import click

from envault.cli import get_vault
from envault.templates import TemplateError, TemplateManager


def _get_manager(base_dir: str) -> TemplateManager:
    return TemplateManager(base_dir)


@click.group(name="template")
def template_group() -> None:
    """Manage environment variable templates."""


@template_group.command("save")
@click.argument("name")
@click.option("--dir", "base_dir", default=".envault", show_default=True)
@click.option("--vault-dir", default=".envault", hidden=True)
@click.password_option(prompt="Vault password")
def save_template(name: str, base_dir: str, vault_dir: str, password: str) -> None:
    """Save current vault contents as a template NAME."""
    vault = get_vault(vault_dir, password)
    manager = _get_manager(base_dir)
    try:
        variables = vault.get_all()
        manager.save_template(name, variables)
        click.echo(f"Template '{name}' saved with {len(variables)} variable(s).")
    except TemplateError as exc:
        raise click.ClickException(str(exc)) from exc


@template_group.command("apply")
@click.argument("name")
@click.option("--dir", "base_dir", default=".envault", show_default=True)
@click.option("--vault-dir", default=".envault", hidden=True)
@click.password_option(prompt="Vault password")
def apply_template(name: str, base_dir: str, vault_dir: str, password: str) -> None:
    """Apply template NAME to the current vault."""
    vault = get_vault(vault_dir, password)
    manager = _get_manager(base_dir)
    try:
        count = manager.apply_template(name, vault)
        click.echo(f"Applied template '{name}': {count} variable(s) written.")
    except TemplateError as exc:
        raise click.ClickException(str(exc)) from exc


@template_group.command("list")
@click.option("--dir", "base_dir", default=".envault", show_default=True)
def list_templates(base_dir: str) -> None:
    """List all saved templates."""
    manager = _get_manager(base_dir)
    names = manager.list_templates()
    if not names:
        click.echo("No templates found.")
    else:
        for name in names:
            click.echo(name)


@template_group.command("delete")
@click.argument("name")
@click.option("--dir", "base_dir", default=".envault", show_default=True)
def delete_template(name: str, base_dir: str) -> None:
    """Delete template NAME."""
    manager = _get_manager(base_dir)
    try:
        manager.delete_template(name)
        click.echo(f"Template '{name}' deleted.")
    except TemplateError as exc:
        raise click.ClickException(str(exc)) from exc
