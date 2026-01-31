from __future__ import annotations

from dataclasses import asdict

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.mapping_service import DEFAULT_MAPPING_NAME, get_active_mapping
from app.importer.dto.import_report import ImportError, ImportReport, ImportStats
from app.importer.pipeline.builder import build_context
from app.importer.pipeline.executor import execute_import
from app.importer.pipeline.validator import validate_context
from app.importer.utils.excel_reader import read_excel_rows


class ImportFailure(Exception):
    pass


def import_proposals_from_excel(
    session: Session,
    file: UploadFile,
    validate_only: bool = False,
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        report = ImportReport(
            ok=False,
            errors=[
                ImportError(
                    type="INVALID_FILE",
                    entity="Import",
                    message="Only .xlsx files are supported.",
                )
            ],
            stats=ImportStats(),
        )
        return asdict(report)

    file.file.seek(0)
    file_bytes = file.file.read()

    try:
        rows = read_excel_rows(file_bytes, sheet_name="Grid 1")
    except Exception as exc:  # noqa: BLE001
        report = ImportReport(
            ok=False,
            errors=[
                ImportError(
                    type="EXCEL_ERROR",
                    entity="Import",
                    message=str(exc),
                )
            ],
            stats=ImportStats(),
        )
        return asdict(report)

    mapping = get_active_mapping(session, DEFAULT_MAPPING_NAME)
    # encerra transação implícita aberta apenas por SELECTs
    if session.in_transaction() and not session.new and not session.dirty:
        session.rollback()
    ctx = build_context(rows, mapping, session)
    report = validate_context(ctx)

    if validate_only or not report.ok:
        return asdict(report)

    report = execute_import(ctx)
    return asdict(report)
