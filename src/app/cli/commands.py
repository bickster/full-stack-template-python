"""CLI commands."""

import asyncio

import click

from app.db.init_db import init_db


@click.group()
def cli() -> None:
    """Application CLI commands."""
    pass


@cli.command()
def init_database() -> None:
    """Initialize the database with default data."""
    click.echo("Initializing database...")
    asyncio.run(init_db())
    click.echo("Database initialization complete!")


if __name__ == "__main__":
    cli()
