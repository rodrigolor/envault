"""CLI commands for the live environment diff watcher."""

import time
import click
from envault.cli import get_vault
from envault.env_diff_watch import EnvDiffWatcher, EnvDiffWatchError


@click.group("watch-diff")
def watch_diff_group():
    """Watch vault for live environment variable changes."""


@watch_diff_group.command("start")
@click.option("--interval", default=5.0, show_default=True, help="Poll interval in seconds.")
@click.option("--profile", default="default", show_default=True)
@click.option("--password", prompt=True, hide_input=True)
def start_watch(interval: float, profile: str, password: str):
    """Start watching the vault for changes (runs until Ctrl+C)."""
    vault = get_vault(profile, password)
    watcher = EnvDiffWatcher(vault, interval=interval)

    def on_added(payload):
        for k, v in payload.items():
            click.secho(f"[+] ADDED    {k}={v}", fg="green")

    def on_modified(payload):
        for k, (old, new) in payload.items():
            click.secho(f"[~] MODIFIED {k}: {old!r} -> {new!r}", fg="yellow")

    def on_removed(payload):
        for k in payload:
            click.secho(f"[-] REMOVED  {k}", fg="red")

    watcher.on("added", on_added)
    watcher.on("modified", on_modified)
    watcher.on("removed", on_removed)

    click.echo(f"Watching vault '{profile}' every {interval}s. Press Ctrl+C to stop.")
    try:
        watcher.start()
        while watcher.is_running:
            time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        click.echo("\nStopping watcher.")
        watcher.stop()
    except EnvDiffWatchError as exc:
        click.secho(f"Error: {exc}", fg="red", err=True)
        raise SystemExit(1)
