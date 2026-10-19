import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def crear_engine(database_url: str | None = None) -> Engine:
    url = database_url if database_url is not None else os.getenv("DATABASE_URL")
    if not url:
        raise ValueError(
            "Configura DATABASE_URL con la URL de conexión a PostgreSQL."
        )
    if not url.startswith(("postgresql://", "postgresql+")):
        raise ValueError("DATABASE_URL debe usar el dialecto PostgreSQL.")

    return create_engine(url, pool_pre_ping=True)
