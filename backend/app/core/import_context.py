from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from sqlalchemy.orm import Session, SessionTransaction

from app.importer.dto.import_report import ImportError

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.customer_recipient import CustomerRecipient
    from app.models.owner import Owner
    from app.models.product import Product
    from app.models.proposal_type import ProposalType
    from app.models.team import Team


@dataclass(frozen=True)
class RawRow:
    row_number: int
    proposal_id: int | None
    detail_has_values: bool
    proposal_values: dict[str, Any]
    detail_values: dict[str, Any] | None
    lookup_values: dict[str, dict[str, Any]]


class ImportContext:
    def __init__(self, session: Session, mapping: dict[str, Any] | None = None) -> None:
        self.session = session
        self.mapping = mapping or {}

        self.raw_rows: list[RawRow] = []
        self.proposals: dict[int, dict[str, Any]] = {}
        self.proposal_details: list[dict[str, Any]] = []

        # Distinct input rows from Excel
        self.customer_rows: dict[int, dict[str, Any]] = {}
        self.recipient_rows: dict[tuple[int, str], dict[str, Any]] = {}
        self.product_rows: dict[str, dict[str, Any]] = {}
        self.proposal_type_rows: dict[str, dict[str, Any]] = {}
        self.team_rows: dict[str, dict[str, Any]] = {}
        self.owner_rows: dict[str, dict[str, Any]] = {}

        # ORM caches for idempotent get-or-create
        self.customers: dict[int, Customer] = {}
        self.recipients: dict[tuple[int, str], CustomerRecipient] = {}
        self.products: dict[str, Product] = {}
        self.proposal_types: dict[str, ProposalType] = {}
        self.teams: dict[str, Team] = {}
        self.owners: dict[str, Owner] = {}

        self.errors: list[ImportError] = []
        self.warnings: list[str] = []

        self._tx: SessionTransaction | None = None

    def begin(self) -> "ImportContext":
        if self._tx is None:
            self._tx = self.session.begin()
        return self

    def __enter__(self) -> "ImportContext":
        if self._tx is None:
            self.begin()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self._tx is None:
            return False
        if exc_type is None:
            self._tx.commit()
        else:
            self._tx.rollback()
        self._tx = None
        return False

    def commit(self) -> None:
        if self._tx is None:
            return
        self._tx.commit()
        self._tx = None

    def rollback(self) -> None:
        if self._tx is None:
            return
        self._tx.rollback()
        self._tx = None
