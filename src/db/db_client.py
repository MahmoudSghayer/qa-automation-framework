"""
DatabaseClient — SQLAlchemy engine wrapper.

Note on the demo:
    The public OrangeHRM demo does NOT expose its database. This module
    is wired up so that when the framework runs against a real env (your
    company's staging), DB validation tests "just work". For demo runs,
    DB tests are auto-skipped via the `db_enabled` fixture in conftest.

Why SQLAlchemy core (not ORM):
    Tests should issue explicit SQL — clearer intent, easier to review.
    ORM models add maintenance burden the QA team rarely benefits from.
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from src.core.exceptions import DatabaseError
from src.utils.logger import logger


class DatabaseClient:
    def __init__(self, *, host: str, port: int, name: str, user: str, password: str, pool_size: int = 5, read_only: bool = False):
        self.read_only = read_only
        url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"
        self._engine: Engine = create_engine(
            url,
            pool_size=pool_size,
            pool_pre_ping=True,         # heals dead connections
            pool_recycle=1800,
            future=True,
        )
        logger.info(f"DB engine ready → {host}:{port}/{name} (read_only={read_only})")

    @contextmanager
    def connect(self) -> Iterator[Any]:
        try:
            with self._engine.connect() as conn:
                yield conn
        except SQLAlchemyError as e:
            raise DatabaseError(f"Database error: {e}") from e

    # ---------------------------------------------------------- queries --
    def fetch_one(self, sql: str, **params: Any) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(text(sql), params).mappings().first()
            return dict(row) if row else None

    def fetch_all(self, sql: str, **params: Any) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

    def execute(self, sql: str, **params: Any) -> int:
        if self.read_only:
            raise DatabaseError("Refusing to execute write query: client is read_only")
        with self.connect() as conn:
            with conn.begin():
                result = conn.execute(text(sql), params)
                return result.rowcount

    def close(self) -> None:
        self._engine.dispose()
