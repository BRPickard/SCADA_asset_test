"""Database setup for SQLite persistence with SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import DB_PATH


class Base(DeclarativeBase):
    """Declarative base class."""


def get_engine(echo: bool = False):
    return create_engine(f"sqlite:///{DB_PATH}", echo=echo, future=True)


SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    from src.models.tables import (  # pylint: disable=import-outside-toplevel
        AssetInstance,
        EnrichmentEvidence,
        MaintenanceSchedule,
        ProductMaster,
        ReviewQueue,
    )

    engine = get_engine()
    Base.metadata.create_all(bind=engine)
