"""CLI commands for compliance policy management."""

from __future__ import annotations

import click

from envault.env_compliance import ComplianceError, ComplianceManager


def _get_manager(ctx: click.Context) -> ComplianceManager:
    vault_dir = ctx.obj.get("vault_dir", ".envault")
    return ComplianceManager(vault_dir)


@click.group("compliance")
def compliance_group() -> None:
    """Manage compliance policies for environment variables."""


@compliance_group.command("set")
@click.argument("rule")
@click.argument("value")
@click.pass_context
def set_policy(ctx: click.Context, rule: str, value: str) -> None:
    """Set a compliance policy rule."""
    mgr = _get_manager(ctx)
    parsed: object = value
    if value.lower() in ("true", "false"):
        parsed = value.lower() == "true"
    elif value.isdigit():
        parsed = int(value)
    try:
        mgr.set_policy(rule, parsed)
        click.echo(f"Policy '{rule}' set to '{parsed}'.")
    except ComplianceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@compliance_group.command("remove")
@click.argument("rule")
@click.pass_context
def remove_policy(ctx: click.Context, rule: str) -> None:
    """Remove a compliance policy rule."""
    mgr = _get_manager(ctx)
    try:
        mgr.remove_policy(rule)
        click.echo(f"Policy '{rule}' removed.")
    except ComplianceError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@compliance_group.command("list")
@click.pass_context
def list_policies(ctx: click.Context) -> None:
    """List all active compliance policies."""
    mgr = _get_manager(ctx)
    policies = mgr.list_policies()
    if not policies:
        click.echo("No compliance policies defined.")
        return
    for rule, value in policies.items():
        click.echo(f"  {rule}: {value}")


@compliance_group.command("check")
@click.pass_context
def run_check(ctx: click.Context) -> None:
    """Run compliance checks against current vault variables."""
    from envault.cli import get_vault  # avoid circular import
    mgr = _get_manager(ctx)
    vault = get_vault(ctx)
    variables = vault.get_all()
    result = mgr.check(variables)
    if result.is_compliant:
        click.echo(click.style(result.summary(), fg="green"))
    else:
        click.echo(click.style(result.summary(), fg="red"))
        for v in result.violations:
            click.echo(f"  - {v}")
        raise SystemExit(1)
