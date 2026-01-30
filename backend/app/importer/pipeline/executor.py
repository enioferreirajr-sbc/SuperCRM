from __future__ import annotations

from dataclasses import replace
from sqlalchemy.orm import Session

from app.importer.context.import_context import ImportContext
from app.importer.dto.import_report import ImportError, ImportReport
from app.importer.pipeline.validator import build_stats
from app.importer.repositories.lookup_repository import (
    insert_customer_recipients,
    insert_customers,
    insert_named_values,
)
from app.importer.repositories.proposals_repository import upsert_proposals_and_details
from app.models.owner import Owner
from app.models.product import Product
from app.models.proposal_type import ProposalType
from app.models.team import Team


def execute_import(ctx: ImportContext, session: Session) -> ImportReport:
    report = ImportReport(
        ok=not ctx.errors,
        errors=list(ctx.errors),
        stats=build_stats(ctx),
        warnings=ctx.warnings or None,
    )
    if ctx.errors:
        return report

    try:
        with session.begin():
            insert_customers(session, ctx.customers)
            insert_customer_recipients(session, ctx.customer_recipients)
            insert_named_values(session, Product, "product_name", ctx.products.keys())
            insert_named_values(session, ProposalType, "proposal_type_name", ctx.proposal_types.keys())
            insert_named_values(session, Team, "team_name", ctx.teams.keys())
            insert_named_values(session, Owner, "owner_name", ctx.owners.keys())
            upsert_proposals_and_details(session, ctx.proposals, ctx.proposal_details)
    except Exception as exc:  # noqa: BLE001
        report = replace(
            report,
            ok=False,
            errors=report.errors
            + [
                ImportError(
                    type="DB_ERROR",
                    entity="Import",
                    message=str(exc),
                )
            ],
        )
    return report
