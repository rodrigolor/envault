"""CLI commands for managing vault notifications."""

from __future__ import annotations

from pathlib import Path

import click

from envault.notifications import NotificationError, NotificationManager


def _get_manager(base_dir: str) -> NotificationManager:
    config_path = Path(base_dir) / "notifications.json"
    return NotificationManager(config_path)


@click.group("notify")
def notification_group() -> None:
    """Manage vault event notifications."""


@notification_group.command("webhook")
@click.argument("event_type")
@click.argument("url")
@click.option("--dir", "base_dir", default=".envault", show_default=True)
def set_webhook(event_type: str, url: str, base_dir: str) -> None:
    """Register a webhook URL for an event type."""
    try:
        mgr = _get_manager(base_dir)
        mgr.configure_webhook(event_type, url)
        click.echo(f"Webhook registered for '{event_type}': {url}")
    except NotificationError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@notification_group.command("list")
@click.option("--dir", "base_dir", default=".envault", show_default=True)
def list_webhooks(base_dir: str) -> None:
    """List all configured webhooks."""
    mgr = _get_manager(base_dir)
    webhooks = mgr.get_webhooks()
    if not webhooks:
        click.echo("No webhooks configured.")
        return
    for event_type, url in webhooks.items():
        click.echo(f"  {event_type}: {url}")


@notification_group.command("remove")
@click.argument("event_type")
@click.option("--dir", "base_dir", default=".envault", show_default=True)
def remove_webhook(event_type: str, base_dir: str) -> None:
    """Remove a webhook for an event type."""
    mgr = _get_manager(base_dir)
    mgr.clear_webhook(event_type)
    click.echo(f"Webhook for '{event_type}' removed.")
