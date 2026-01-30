from __future__ import annotations

from typing import Any


def get_entity_columns(mapping: dict[str, Any], entity_name: str) -> dict[str, Any]:
    return mapping.get("entities", {}).get(entity_name, {}).get("columns", {})


def get_lookup_columns(mapping: dict[str, Any], lookup_name: str) -> dict[str, Any]:
    return mapping.get("lookups", {}).get(lookup_name, {}).get("columns", {})


def get_proposal_key(mapping: dict[str, Any]) -> str:
    return (
        mapping.get("entities", {})
        .get("Proposal", {})
        .get("business_key", "proposal_id")
    )


def get_required_fields(columns: dict[str, Any]) -> list[str]:
    return [name for name, spec in columns.items() if spec.get("required")]
