from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg import Connection

from app.db.settings import get_database_url


@contextmanager
def connect(database_url: str | None = None) -> Iterator[Connection]:
    """Open a database connection on demand.

    Nothing in this module connects at import time; callers opt in explicitly.
    """

    with psycopg.connect(database_url or get_database_url()) as connection:
        yield connection
