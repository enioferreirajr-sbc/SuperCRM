from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_MAPPING_NAME = "business_proposals"
DEFAULT_MAPPING_VERSION = "1.0.0"


@dataclass(frozen=True)
class BootstrapMapping:
    name: str
    version: str
    mapping: Any
    raw_json: str


def _bootstrap_path() -> Path:
    return Path(__file__).resolve().parent / "mappings" / "business_proposals.v1.json"


def validate_mapping_structure(mapping: Any) -> None:
    if not isinstance(mapping, (dict, list)):
        raise ValueError("Mapping JSON must be an object or array.")
    if isinstance(mapping, dict):
        if "name" in mapping and not isinstance(mapping["name"], str):
            raise ValueError("Mapping JSON 'name' must be a string.")
        if "version" in mapping and not isinstance(mapping["version"], str):
            raise ValueError("Mapping JSON 'version' must be a string.")


def load_bootstrap_mapping() -> BootstrapMapping:
    path = _bootstrap_path()
    try:
        raw_json = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"Bootstrap mapping file not found: {path}") from exc
    mapping = json.loads(raw_json)
    validate_mapping_structure(mapping)

    if isinstance(mapping, dict):
        name = mapping.get("name", DEFAULT_MAPPING_NAME)
        version = mapping.get("version", DEFAULT_MAPPING_VERSION)
    else:
        name = DEFAULT_MAPPING_NAME
        version = DEFAULT_MAPPING_VERSION

    return BootstrapMapping(name=name, version=version, mapping=mapping, raw_json=raw_json)
