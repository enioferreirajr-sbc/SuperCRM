from __future__ import annotations

from app.core.import_context import ImportContext
from app.importer.contracts.mapping_contract import (
    get_entity_columns,
    get_proposal_key,
)
from app.importer.dto.import_report import ImportError, ImportReport, ImportStats
from app.importer.utils.normalization import is_empty


def build_stats(ctx: ImportContext) -> ImportStats:
    return ImportStats(
        total_rows=len(ctx.raw_rows),
        proposals_found=len(ctx.proposals),
        details_found=len(ctx.proposal_details),
        customers_distinct=len(ctx.customer_rows),
        recipients_distinct=len(ctx.recipient_rows),
        products_distinct=len(ctx.product_rows),
        teams_distinct=len(ctx.team_rows),
        owners_distinct=len(ctx.owner_rows),
    )


def validate_context(ctx: ImportContext) -> ImportReport:
    errors = list(ctx.errors)

    proposal_columns = get_entity_columns(ctx.mapping, "Proposal")
    proposal_key = get_proposal_key(ctx.mapping)

    required_proposal_fields = ["proposal_id", "proposal_name"]

    for raw_row in ctx.raw_rows:
        for field_name in required_proposal_fields:
            value = raw_row.proposal_values.get(field_name)
            if is_empty(value):
                source = proposal_columns.get(field_name, {}).get("source", field_name)
                errors.append(
                    ImportError(
                        type="MISSING_REQUIRED",
                        entity="Proposal",
                        row_number=raw_row.row_number,
                        field=source,
                        message=f"Row {raw_row.row_number}: missing required field '{source}'.",
                    )
                )

        if raw_row.detail_has_values and is_empty(raw_row.proposal_values.get(proposal_key)):
            errors.append(
                ImportError(
                    type="MISSING_REQUIRED",
                    entity="ProposalDetail",
                    row_number=raw_row.row_number,
                    field=proposal_key,
                    message=f"Row {raw_row.row_number}: missing proposal_id.",
                )
            )

    proposal_ids = set(ctx.proposals.keys())
    for detail in ctx.proposal_details:
        proposal_id = detail.get("proposal_id")
        if proposal_id is not None and proposal_id not in proposal_ids:
            errors.append(
                ImportError(
                    type="INVALID_RELATION",
                    entity="ProposalDetail",
                    message=f"Detail references missing proposal_id {proposal_id}.",
                    sample_value=proposal_id,
                )
            )

    return ImportReport(
        ok=not errors,
        errors=errors,
        stats=build_stats(ctx),
        warnings=ctx.warnings or None,
    )
