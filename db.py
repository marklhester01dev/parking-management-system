import sqlite3
from pathlib import Path

import click
from flask import current_app, g

SCHEMA = Path(__file__).with_name("schema.sql")


def get_db():
    """One connection per request, rows accessible by column name."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db(reset=False):
    conn = get_db()
    if reset:
        conn.executescript(
            "DROP TABLE IF EXISTS parking_transactions;"
            "DROP TABLE IF EXISTS parking_slots;"
            "DROP TABLE IF EXISTS vehicles;"
        )
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))


@click.command("init-db")
@click.option("--reset", is_flag=True, help="Drop existing tables first (deletes all data).")
def init_db_command(reset):
    """Create the database tables from schema.sql."""
    init_db(reset)
    click.echo("Database reset and initialized." if reset else "Database initialized.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)