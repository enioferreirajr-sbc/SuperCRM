from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ImportError:
    type: str
    entity: str
    message: str
    row_number: int | None = None
    field: str | None = None
    sample_value: Any | None = None


@dataclass(frozen=True)
class ImportStats:
    total_rows: int = 0
    proposals_found: int = 0
    details_found: int = 0
    customers_distinct: int = 0
    recipients_distinct: int = 0
    products_distinct: int = 0
    teams_distinct: int = 0
    owners_distinct: int = 0


@dataclass(frozen=True)
class ImportReport:
    ok: bool
    errors: list[ImportError] = field(default_factory=list)
    stats: ImportStats = field(default_factory=ImportStats)
    warnings: list[str] | None = None
    preview: dict[str, Any] | None = None
