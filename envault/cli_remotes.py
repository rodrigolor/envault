"""CLI commands for managing sync remotes."""

from __future__ import annotations

from pathlib import Path

import click

from envault.remotes import RemoteError, RemoteManager


def _get_manager(base_dir: str) -> RemoteManager:
    return RemoteManager(Path(base_dir))


@click.group("remote")
def remote_group() -> None:
    """Manage remote sync backends."""


@remote_group.command("add")
@click.argument("name")
@click.option("--type", "remote_type", required=True, help="Backend type (file, s3, gcs).")
@click.option("--url", required=True, help="Remote URL or path.")
@click.option("--base-dir", default=".envault", show_default=True)
def add_remote(name: str, remote_type: str, url: str, base_dir: str) -> None:
    """Register a new remote backend."""
    mgr = _get_manager(base_dir)
    try:
        mgr.add(name, remote_type, url)
        click.echo(f"Remote '{name}' added ({remote_type}: {url}).")
    except RemoteError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@remote_group.command("remove")
@click.argument("name")
@click.option("--base-dir", default=".envault", show_default=True)
def remove_remote(name: str, base_dir: str) -> None:
    """Remove a registered remote."""
    mgr = _get_manager(base_dir)
    try:
        mgr.remove(name)
        click.echo(f"Remote '{name}' removed.")
    except RemoteError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@remote_group.command("list")
@click.option("--base-dir", default=".envault", show_default=True)
def list_remotes(base_dir: str) -> None:
    """List all registered remotes."""
    mgr = _get_manager(base_dir)
    names = mgr.list_remotes()
    if not names:
        click.echo("No remotes configured.")
        return
    for name in names:
        info = mgr.get(name)
        click.echo(f"{name}  [{info['type']}]  {info['url']}")


@remote_group.command("show")
@click.argument("name")
@click.option("--base-dir", default=".envault", show_default=True)
def show_remote(name: str, base_dir: str) -> None:
    """Show details of a remote."""
    mgr = _get_manager(base_dir)
    try:
        info = mgr.get(name)
        for key, value in info.items():
            click.echo(f"{key}: {value}")
    except RemoteError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
