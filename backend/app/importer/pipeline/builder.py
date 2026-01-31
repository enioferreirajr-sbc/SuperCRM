from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.import_context import ImportContext, RawRow
from app.importer.contracts.mapping_contract import (
    get_entity_columns,
    get_lookup_columns,
    get_proposal_key,
)
from app.importer.dto.import_report import ImportError
from app.importer.utils.normalization import (
    is_empty,
    norm_date,
    norm_decimal,
    norm_email,
    norm_int,
    norm_str,
)


_DETAIL_LOOKUP_NAMES = {"Product", "ProposalType", "Team", "Owner"}


def _normalize_value(value: Any, spec: dict[str, Any], *, for_email: bool = False) -> Any:
    raw_value = value
    if is_empty(raw_value) and "default" in spec:
        raw_value = spec["default"]

    value_type = spec.get("type", "string")
    if value_type == "int":
        return norm_int(raw_value)
    if value_type == "decimal":
        return norm_decimal(raw_value)
    if value_type == "date":
        return norm_date(raw_value)
    if value_type == "string":
        return norm_email(raw_value) if for_email else norm_str(raw_value)
    return raw_value


def build_context(
    rows: list[dict[str, Any]],
    mapping: dict[str, Any],
    session: Session,
) -> ImportContext:
    ctx = ImportContext(session=session, mapping=mapping)

    proposal_columns = get_entity_columns(mapping, "Proposal")
    detail_columns = get_entity_columns(mapping, "ProposalDetail")
    proposal_key = get_proposal_key(mapping)

    lookup_columns = {
        "Customer": get_lookup_columns(mapping, "Customer"),
        "CustomerRecipient": get_lookup_columns(mapping, "CustomerRecipient"),
        "Product": get_lookup_columns(mapping, "Product"),
        "ProposalType": get_lookup_columns(mapping, "ProposalType"),
        "Team": get_lookup_columns(mapping, "Team"),
        "Owner": get_lookup_columns(mapping, "Owner"),
    }

    known_sources = set()
    for columns in proposal_columns.values():
        if columns.get("source"):
            known_sources.add(columns["source"])
    for columns in detail_columns.values():
        if columns.get("source"):
            known_sources.add(columns["source"])
    for lookup in lookup_columns.values():
        for columns in lookup.values():
            if columns.get("source"):
                known_sources.add(columns["source"])

    row_sources = set()
    for row in rows:
        row_sources.update(key for key in row.keys() if key != "__rownum__")
    unknown_sources = sorted(source for source in row_sources if source not in known_sources)
    if unknown_sources:
        ctx.warnings.append(f"Unknown columns ignored: {', '.join(unknown_sources[:10])}")

    detail_signal_sources = [
        spec.get("source")
        for spec in detail_columns.values()
        if spec.get("source")
    ]
    for lookup_name in _DETAIL_LOOKUP_NAMES:
        for spec in lookup_columns.get(lookup_name, {}).values():
            if spec.get("source"):
                detail_signal_sources.append(spec["source"])

    for row in rows:
        row_number = int(row.get("__rownum__", 0))
        if all(is_empty(row.get(source)) for source in known_sources):
            continue

        proposal_values: dict[str, Any] = {}
        for field_name, spec in proposal_columns.items():
            source = spec.get("source")
            if not source:
                continue
            try:
                proposal_values[field_name] = _normalize_value(row.get(source), spec)
            except Exception as exc:  # noqa: BLE001
                ctx.errors.append(
                    ImportError(
                        type="INVALID_TYPE",
                        entity="Proposal",
                        row_number=row_number,
                        field=source,
                        message=str(exc),
                        sample_value=row.get(source),
                    )
                )
                proposal_values[field_name] = None

        detail_has_values = any(
            not is_empty(row.get(source)) for source in detail_signal_sources
        )

        detail_values: dict[str, Any] | None = None
        if detail_has_values:
            detail_values = {}
            for field_name, spec in detail_columns.items():
                source = spec.get("source")
                if not source:
                    continue
                try:
                    detail_values[field_name] = _normalize_value(row.get(source), spec)
                except Exception as exc:  # noqa: BLE001
                    ctx.errors.append(
                        ImportError(
                            type="INVALID_TYPE",
                            entity="ProposalDetail",
                            row_number=row_number,
                            field=source,
                            message=str(exc),
                            sample_value=row.get(source),
                        )
                    )
                    detail_values[field_name] = None

        lookup_values: dict[str, dict[str, Any]] = {}
        for lookup_name, columns in lookup_columns.items():
            values: dict[str, Any] = {}
            for field_name, spec in columns.items():
                source = spec.get("source")
                if not source:
                    continue
                try:
                    for_email = lookup_name == "CustomerRecipient" and field_name == "recipient_email"
                    values[field_name] = _normalize_value(
                        row.get(source),
                        spec,
                        for_email=for_email,
                    )
                except Exception as exc:  # noqa: BLE001
                    ctx.errors.append(
                        ImportError(
                            type="INVALID_TYPE",
                            entity=lookup_name,
                            row_number=row_number,
                            field=source,
                            message=str(exc),
                            sample_value=row.get(source),
                        )
                    )
                    values[field_name] = None
            lookup_values[lookup_name] = values

        proposal_id = proposal_values.get(proposal_key)
        raw_row = RawRow(
            row_number=row_number,
            proposal_id=proposal_id,
            detail_has_values=detail_has_values,
            proposal_values=proposal_values,
            detail_values=detail_values,
            lookup_values=lookup_values,
        )
        ctx.raw_rows.append(raw_row)

        if proposal_id is not None:
            if proposal_id not in ctx.proposals:
                ctx.proposals[proposal_id] = proposal_values
            else:
                existing = ctx.proposals[proposal_id]
                for key, value in proposal_values.items():
                    if existing.get(key) is None and value is not None:
                        existing[key] = value

        if detail_has_values and proposal_id is not None and detail_values is not None:
            detail_record = {"proposal_id": proposal_id, **detail_values}
            detail_record["product_name"] = lookup_values.get("Product", {}).get("product_name")
            detail_record["proposal_type_name"] = lookup_values.get("ProposalType", {}).get(
                "proposal_type_name"
            )
            detail_record["team_name"] = lookup_values.get("Team", {}).get("team_name")
            detail_record["owner"] = lookup_values.get("Owner", {}).get("owner_name")
            ctx.proposal_details.append(detail_record)

        customer_data = lookup_values.get("Customer", {})
        main_contract_id = customer_data.get("main_contract_id")
        if not is_empty(main_contract_id):
            contract_id = int(main_contract_id)
            if contract_id not in ctx.customer_rows:
                ctx.customer_rows[contract_id] = {
                    "main_contract_id": contract_id,
                    "customer_reference": customer_data.get("customer_reference"),
                }

        recipient_data = lookup_values.get("CustomerRecipient", {})
        recipient_email = recipient_data.get("recipient_email")
        recipient_name = recipient_data.get("recipient_name")
        if not is_empty(main_contract_id) and not is_empty(recipient_email):
            recipient_key = (int(main_contract_id), str(recipient_email))
            if recipient_key not in ctx.recipient_rows:
                ctx.recipient_rows[recipient_key] = {
                    "main_contract_id": int(main_contract_id),
                    "recipient_email": str(recipient_email),
                    "recipient_name": recipient_name,
                    "cellphone": recipient_data.get("cellphone"),
                }

        product_name = lookup_values.get("Product", {}).get("product_name")
        if not is_empty(product_name):
            ctx.product_rows[str(product_name)] = {"product_name": str(product_name)}

        proposal_type_name = lookup_values.get("ProposalType", {}).get("proposal_type_name")
        if not is_empty(proposal_type_name):
            ctx.proposal_type_rows[str(proposal_type_name)] = {
                "proposal_type_name": str(proposal_type_name)
            }

        team_name = lookup_values.get("Team", {}).get("team_name")
        if not is_empty(team_name):
            ctx.team_rows[str(team_name)] = {"team_name": str(team_name)}

        owner_name = lookup_values.get("Owner", {}).get("owner_name")
        if not is_empty(owner_name):
            ctx.owner_rows[str(owner_name)] = {"owner_name": str(owner_name)}

    return ctx
