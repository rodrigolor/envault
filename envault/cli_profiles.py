"""CLI commands for profile management, registered as a sub-group on the main CLI."""

from __future__ import annotations

from pathlib import Path

import click

from envault.profiles import DEFAULT_PROFILE, ProfileManager

_DEFAULT_BASE = Path.home() / ".envault"


def _get_manager(base_dir: Path) -> ProfileManager:
    return ProfileManager(base_dir)


@click.group("profile")
@click.option(
    "--base-dir",
    default=str(_DEFAULT_BASE),
    show_default=True,
    help="Directory where vault files are stored.",
)
@click.pass_context
def profile_group(ctx: click.Context, base_dir: str) -> None:
    """Manage envault profiles."""
    ctx.ensure_object(dict)
    ctx.obj["manager"] = _get_manager(Path(base_dir))


@profile_group.command("list")
@click.pass_context
def list_profiles(ctx: click.Context) -> None:
    """List all available profiles."""
    manager: ProfileManager = ctx.obj["manager"]
    profiles = manager.list_profiles()
    if not profiles:
        click.echo("No profiles found.")
        return
    for name in profiles:
        marker = " (default)" if name == DEFAULT_PROFILE else ""
        click.echo(f"  {name}{marker}")


@profile_group.command("create")
@click.argument("name")
@click.pass_context
def create_profile(ctx: click.Context, name: str) -> None:
    """Create a new profile named NAME."""
    manager: ProfileManager = ctx.obj["manager"]
    try:
        manager.create_profile(name)
        click.echo(f"Profile '{name}' created.")
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@profile_group.command("delete")
@click.argument("name")
@click.pass_context
def delete_profile(ctx: click.Context, name: str) -> None:
    """Delete profile NAME from the index."""
    manager: ProfileManager = ctx.obj["manager"]
    try:
        manager.delete_profile(name)
        click.echo(f"Profile '{name}' deleted.")
    except (ValueError, KeyError) as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
