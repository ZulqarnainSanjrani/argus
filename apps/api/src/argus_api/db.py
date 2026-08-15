import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def database_url() -> str | None:
    return os.getenv("ARGUS_DATABASE_URL")


def session_factory(url: str | None = None):
    resolved = url or database_url()
    if not resolved:
        return None
    engine = create_engine(resolved, pool_pre_ping=True)
    return sessionmaker(engine, expire_on_commit=False)
