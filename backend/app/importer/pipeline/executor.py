from __future__ import annotations

from dataclasses import replace

from app.core.import_context import ImportContext
from app.importer.dto.import_report import ImportError, ImportReport
from app.importer.pipeline.validator import build_stats
from app.importer.repositories.lookup_repository import (
    get_or_create_customer,
    get_or_create_customer_recipient,
    get_or_create_owner,
    get_or_create_product,
    get_or_create_proposal_type,
    get_or_create_team,
)
from app.importer.repositories.proposals_repository import (
    import_proposal_details,
    import_proposals,
)


def import_customers(ctx: ImportContext) -> None:
    for data in ctx.customer_rows.values():
        get_or_create_customer(
            ctx,
            data.get("main_contract_id"),
            data.get("customer_reference"),
        )


def import_recipients(ctx: ImportContext) -> None:
    for data in ctx.recipient_rows.values():
        get_or_create_customer_recipient(
            ctx,
            data.get("main_contract_id"),
            data.get("recipient_email"),
            data.get("recipient_name"),
            data.get("cellphone"),
        )


def import_products(ctx: ImportContext) -> None:
    for name in ctx.product_rows.keys():
        get_or_create_product(ctx, name)


def import_proposal_types(ctx: ImportContext) -> None:
    for name in ctx.proposal_type_rows.keys():
        get_or_create_proposal_type(ctx, name)


def import_teams(ctx: ImportContext) -> None:
    for name in ctx.team_rows.keys():
        get_or_create_team(ctx, name)


def import_owners(ctx: ImportContext) -> None:
    for name in ctx.owner_rows.keys():
        get_or_create_owner(ctx, name)


def execute_import(ctx: ImportContext) -> ImportReport:
    report = ImportReport(
        ok=not ctx.errors,
        errors=list(ctx.errors),
        stats=build_stats(ctx),
        warnings=ctx.warnings or None,
    )
    if ctx.errors:
        return report

    try:
        with ctx.begin() as import_ctx:
            import_customers(import_ctx)
            import_recipients(import_ctx)
            import_products(import_ctx)
            import_proposal_types(import_ctx)
            import_teams(import_ctx)
            import_owners(import_ctx)
            import_proposals(import_ctx)
            import_proposal_details(import_ctx)
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
