from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.importer.dto.import_report import ImportError


@dataclass(frozen=True)
class RawRow:
    row_number: int
    proposal_id: int | None
    detail_has_values: bool
    proposal_values: dict[str, Any]
    detail_values: dict[str, Any] | None
    lookup_values: dict[str, dict[str, Any]]


@dataclass
class ImportContext:
    mapping: dict[str, Any]
    raw_rows: list[RawRow] = field(default_factory=list)
    customers: dict[int, dict[str, Any]] = field(default_factory=dict)
    customer_recipients: dict[tuple[int, str], dict[str, Any]] = field(default_factory=dict)
    products: dict[str, dict[str, Any]] = field(default_factory=dict)
    proposal_types: dict[str, dict[str, Any]] = field(default_factory=dict)
    teams: dict[str, dict[str, Any]] = field(default_factory=dict)
    owners: dict[str, dict[str, Any]] = field(default_factory=dict)
    proposals: dict[int, dict[str, Any]] = field(default_factory=dict)
    proposal_details: list[dict[str, Any]] = field(default_factory=list)
    errors: list[ImportError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
