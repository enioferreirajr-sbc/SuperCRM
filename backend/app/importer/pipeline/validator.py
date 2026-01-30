from __future__ import annotations

from app.importer.context.import_context import ImportContext
from app.importer.contracts.mapping_contract import (
    get_entity_columns,
    get_proposal_key,
    get_required_fields,
)
from app.importer.dto.import_report import ImportError, ImportReport, ImportStats
from app.importer.utils.normalization import is_empty


def build_stats(ctx: ImportContext) -> ImportStats:
    return ImportStats(
        total_rows=len(ctx.raw_rows),
        proposals_found=len(ctx.proposals),
        details_found=len(ctx.proposal_details),
        customers_distinct=len(ctx.customers),
        recipients_distinct=len(ctx.customer_recipients),
        products_distinct=len(ctx.products),
        teams_distinct=len(ctx.teams),
        owners_distinct=len(ctx.owners),
    )


def validate_context(ctx: ImportContext) -> ImportReport:
    errors = list(ctx.errors)

    proposal_columns = get_entity_columns(ctx.mapping, "Proposal")
    detail_columns = get_entity_columns(ctx.mapping, "ProposalDetail")
    proposal_key = get_proposal_key(ctx.mapping)

    required_proposal_fields = get_required_fields(proposal_columns)
    required_detail_fields = get_required_fields(detail_columns)

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

        if raw_row.detail_has_values:
            if is_empty(raw_row.proposal_values.get(proposal_key)):
                errors.append(
                    ImportError(
                        type="MISSING_REQUIRED",
                        entity="ProposalDetail",
                        row_number=raw_row.row_number,
                        field=proposal_key,
                        message=f"Row {raw_row.row_number}: missing proposal_id.",
                    )
                )

            for field_name in required_detail_fields:
                value = (raw_row.detail_values or {}).get(field_name)
                if is_empty(value):
                    source = detail_columns.get(field_name, {}).get("source", field_name)
                    errors.append(
                        ImportError(
                            type="MISSING_REQUIRED",
                            entity="ProposalDetail",
                            row_number=raw_row.row_number,
                            field=source,
                            message=f"Row {raw_row.row_number}: missing required field '{source}'.",
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
