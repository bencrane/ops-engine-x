"""Database connection helper.

Uses OPEX_DB_URL_POOLED (the pooled Postgres connection string from Doppler)
for runtime app traffic. Keeps psycopg usage explicit so the app stays
Supabase-port-agnostic.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg

from app.config import require


@contextmanager
def connect() -> Iterator[psycopg.Connection]:
    dsn = require("opex_db_url_pooled")
    with psycopg.connect(dsn, autocommit=False) as conn:
        yield conn
