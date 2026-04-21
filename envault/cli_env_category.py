import click
from pathlib import Path
from envault.env_category import CategoryManager, CategoryError


def _get_manager(ctx: click.Context) -> CategoryManager:
    vault_dir = ctx.obj.get("vault_dir", ".envault")
    return CategoryManager(vault_dir)


@click.group("category")
def category_group() -> None:
    """Manage categories for environment variable keys."""


@category_group.command("assign")
@click.argument("key")
@click.argument("category")
@click.pass_context
def assign_category(ctx: click.Context, key: str, category: str) -> None:
    """Assign KEY to CATEGORY."""
    mgr = _get_manager(ctx)
    try:
        mgr.assign(key, category)
        click.echo(f"Assigned '{key}' to category '{category}'.")
    except CategoryError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@category_group.command("unassign")
@click.argument("key")
@click.pass_context
def unassign_category(ctx: click.Context, key: str) -> None:
    """Remove category assignment from KEY."""
    mgr = _get_manager(ctx)
    try:
        mgr.unassign(key)
        click.echo(f"Removed category from '{key}'.")
    except CategoryError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@category_group.command("get")
@click.argument("key")
@click.pass_context
def get_category(ctx: click.Context, key: str) -> None:
    """Show the category assigned to KEY."""
    mgr = _get_manager(ctx)
    cat = mgr.get_category(key)
    if cat is None:
        click.echo(f"'{key}' has no category assigned.")
    else:
        click.echo(cat)


@category_group.command("list")
@click.option("--category", "-c", default=None, help="Filter by category name.")
@click.pass_context
def list_categories(ctx: click.Context, category: str) -> None:
    """List keys and their categories."""
    mgr = _get_manager(ctx)
    if category:
        keys = mgr.list_by_category(category)
        if not keys:
            click.echo(f"No keys in category '{category}'.")
        else:
            for k in sorted(keys):
                click.echo(k)
    else:
        data = mgr.list_all()
        if not data:
            click.echo("No categories assigned.")
        else:
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
