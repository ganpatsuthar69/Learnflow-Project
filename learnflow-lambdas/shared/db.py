"""Lightweight DB connection for Lambda functions using psycopg2."""

import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from .config import config


@contextmanager
def get_connection():
    """Yield a database connection, auto-close on exit."""
    conn = psycopg2.connect(config.DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_cursor(conn):
    """Yield a cursor from an existing connection."""
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
