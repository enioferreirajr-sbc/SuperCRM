from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import insert, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.bootstrap.loader import validate_mapping_structure
from app.models.import_mapping import ImportMapping

DEFAULT_MAPPING_NAME = "business_proposals"
DEFAULT_MAPPING_VERSION = "1.0.0"
BOOTSTRAP_MAPPING_FILENAME = "business_proposals.v1.json"


def _bootstrap_path() -> Path:
    return (
        Path(__file__).resolve().parents[1]
        / "bootstrap"
        / "mappings"
        / BOOTSTRAP_MAPPING_FILENAME
    )


def load_bootstrap_mapping_json() -> dict:
    path = _bootstrap_path()
    try:
        raw_json = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Bootstrap mapping file not found: {path}") from exc
    try:
        mapping = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Bootstrap mapping JSON is invalid: {path}") from exc
    validate_mapping_structure(mapping)
    if not isinstance(mapping, dict):
        raise RuntimeError("Bootstrap mapping JSON must be an object.")
    return mapping


def _deserialize_mapping_payload(payload: Any) -> Any:
    if payload is None:
        raise RuntimeError("Active mapping has no JSON payload.")
    if isinstance(payload, (dict, list)):
        mapping = payload
    else:
        try:
            mapping = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Active mapping JSON is invalid.") from exc
    validate_mapping_structure(mapping)
    return mapping


def _fetch_active_records(session: Session, name: str) -> list[ImportMapping]:
    return (
        session.execute(
            select(ImportMapping).where(
                ImportMapping.name == name,
                ImportMapping.is_active == True,
            )
        )
        .scalars()
        .all()
    )


def ensure_active_mapping(engine: Engine) -> None:
    name = DEFAULT_MAPPING_NAME
    version = DEFAULT_MAPPING_VERSION

    table = ImportMapping.__table__
    with engine.begin() as conn:
        active_records = (
            conn.execute(
                select(table).where(
                    table.c.name == name,
                    table.c.is_active == True,
                )
            )
            .mappings()
            .all()
        )
        if len(active_records) > 1:
            raise RuntimeError(f"Multiple active mappings found for '{name}'.")
        if active_records:
            return

        existing = (
            conn.execute(
                select(table).where(
                    table.c.name == name,
                    table.c.version == version,
                )
            )
            .mappings()
            .first()
        )

        conn.execute(
            update(table)
            .where(table.c.name == name)
            .values(is_active=False)
        )
        if existing is None:
            mapping = load_bootstrap_mapping_json()
            conn.execute(
                insert(table).values(
                    name=name,
                    version=version,
                    mapping_json=json.dumps(mapping),
                    is_active=True,
                )
            )
        else:
            conn.execute(
                update(table)
                .where(
                    table.c.name == name,
                    table.c.version == version,
                )
                .values(is_active=True)
            )

        active_records = (
            conn.execute(
                select(table).where(
                    table.c.name == name,
                    table.c.is_active == True,
                )
            )
            .mappings()
            .all()
        )
        if not active_records:
            raise RuntimeError(f"No active mapping found for '{name}'.")
        if len(active_records) > 1:
            raise RuntimeError(f"Multiple active mappings found for '{name}'.")


def get_active_mapping(session: Session, name: str) -> dict:
    active_records = _fetch_active_records(session, name)
    if not active_records:
        raise RuntimeError(f"No active mapping found for '{name}'.")
    if len(active_records) > 1:
        raise RuntimeError(f"Multiple active mappings found for '{name}'.")
    mapping = _deserialize_mapping_payload(active_records[0].mapping_json)
    if not isinstance(mapping, dict):
        raise RuntimeError("Active mapping JSON must be an object.")
    return mapping
