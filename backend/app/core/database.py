from __future__ import annotations

import urllib.parse
from pathlib import Path
from typing import Generator

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

BASE_ODBC_STRING = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost\\SQLEXPRESS;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

DATABASE_ODBC_STRING = (
    BASE_ODBC_STRING
    + "Database=crm_db;"
)

BASE_PARAMS = urllib.parse.quote_plus(BASE_ODBC_STRING)
DATABASE_PARAMS = urllib.parse.quote_plus(DATABASE_ODBC_STRING)

BASE_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={BASE_PARAMS}"
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={DATABASE_PARAMS}"

engine = None
SessionLocal = None


def create_database_if_not_exists() -> None:
    server_engine = create_engine(BASE_DATABASE_URL, isolation_level="AUTOCOMMIT", future=True)
    try:
        with server_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM sys.databases WHERE name = :name"),
                {"name": "crm_db"},
            ).scalar()
            if not exists:
                connection.execute(text("CREATE DATABASE [crm_db]"))
    finally:
        server_engine.dispose()


def init_engine() -> None:
    global engine, SessionLocal
    if engine is None:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def run_migrations() -> None:
    migrations_path = Path(__file__).resolve().parents[1] / "migrations"
    config = Config()
    config.set_main_option("script_location", str(migrations_path))
    config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))
    command.upgrade(config, "head")


def init_db() -> None:
    create_database_if_not_exists()
    init_engine()
    run_migrations()


def get_db() -> Generator:
    if SessionLocal is None:
        init_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
