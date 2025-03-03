"""Database access: one connection per request, search_path set to the state's schema."""

import psycopg
from psycopg.rows import dict_row

from app.settings import settings


def connect():
    conn = psycopg.connect(settings.database_url, row_factory=dict_row)
    conn.execute(f"SET search_path TO {settings.schema}")
    return conn


def query(conn, sql, params=()):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def query_one(conn, sql, params=()):
    rows = query(conn, sql, params)
    return rows[0] if rows else None


def app_config(conn, key, default=None):
    """A value from app_config, or the default when the key is not set."""
    row = query_one(conn, "SELECT value FROM app_config WHERE key = %s", (key,))
    return row["value"] if row else default
