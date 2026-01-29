import pandas as pd
from typing import Dict, Any, List, Tuple
from decimal import Decimal
from io import BytesIO
import openpyxl
import json
import os
from datetime import datetime
from fastapi import UploadFile, HTTPException
from pymongo import UpdateOne
from bson import Decimal128

from app.core.constants import PROPOSAL_IMPORT_SCHEMA, parse_currency, parse_date
from app.features.proposals.models import BusinessProposal, ProposalItem
from app.features.proposals.schemas import (
    ProposalImportRow, 
    ProposalReadDTO, 
    PaginatedResponse,
    ProposalItemDTO,
    ImportResponse,
    ImportSummary,
    ImportErrorDetail
)
from app.features.proposals.repository import ProposalRepository

LOGS_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# PHASE 1: SYNC PARSING (CPU BOUND)
# -----------------------------------------------------------------------------

def _parse_excel_sync(content: bytes) -> Tuple[List[Dict[str, Any]], List[ImportErrorDetail]]:
    """
    Parses Excel content, maps columns, processes types, and aggregates by ID.
    Returns: (List of proposal dictionaries ready for DB, List of errors)
    """
    errors = []
    
    try:
        df = pd.read_excel(BytesIO(content), dtype=object)
    except Exception as e:
        raise ValueError(f"Failed to read Excel: {str(e)}")

    # 1. Column Mapping & Basic Transofmration
    # We iterate rows and build a list of "Item Dictionaries" first
    raw_items = []
    
    for index, row in df.iterrows():
        line_num = index + 2
        item_data = {}
        
        # Check ID presence using the mapped name or original name? 
        # The SCHEMA keys are Original Names.
        orig_id_col = "Business Proposal ID"
        val_id = row.get(orig_id_col)
        
        if pd.isna(val_id) or str(val_id).strip() == "":
            continue # Skip empty lines
            
        # Parse fields based on Schema
        try:
            for orig_col, config in PROPOSAL_IMPORT_SCHEMA.items():
                val = row.get(orig_col)
                target_field = config["field"]
                target_type = config["type"]
                
                parsed_val = None
                
                if target_type == "int":
                    parsed_val = int(val) if pd.notna(val) else None
                elif target_type == "str":
                    parsed_val = str(val).strip() if pd.notna(val) and val != "" else None
                elif target_type == "currency":
                    parsed_val = parse_currency(val)
                elif target_type == "date":
                    parsed_val = parse_date(val)
                else:
                    parsed_val = val
                
                item_data[target_field] = parsed_val
                
            raw_items.append({"line": line_num, "data": item_data})
            
        except Exception as e:
            errors.append(ImportErrorDetail(
                line_number=line_num, 
                message=f"Parsing Error: {str(e)}",
                value_provided=str(row.to_dict())
            ))

    # 2. Aggregation (Grouping by ID)
    proposals_map: Dict[int, Dict[str, Any]] = {}
    
    for entry in raw_items:
        data = entry["data"]
        p_id = data.get("business_proposal_id")
        
        if p_id not in proposals_map:
            # Initialize Proposal Header (using first row data)
            proposals_map[p_id] = {
                "business_proposal_id": p_id,
                "customer_reference": data.get("customer_reference"),
                "business_proposal_date": data.get("business_proposal_date"),
                "last_status_date": data.get("last_status_date"),
                "funnel_percentage": data.get("funnel_percentage"),
                "business_proposal_name": data.get("business_proposal_name"),
                "business_proposal_status": data.get("business_proposal_status"),
                "last_note": data.get("last_note"),
                "recipient_name": data.get("recipient_name"),
                "recipient_e_mail": data.get("recipient_e_mail"),
                "funnel_percentage_id": data.get("funnel_percentage_id"),
                "aging_business_proposal": data.get("aging_business_proposal"),
                "aging_status": data.get("aging_status"),
                "total_value_aggregated": Decimal(0),
                "items": []
            }
            
        # Update Aggregate Total
        item_sales = data.get("total_sales", Decimal(0))
        proposals_map[p_id]["total_value_aggregated"] += item_sales
        
        # Create Item Object
        # Filter data to only include Item fields? 
        # Models will ignore extras usually, but let's be clean.
        # ProposalItem model fields:
        item_obj = ProposalItem(
            product_name=data.get("product_name") or "Unknown",
            proposal_type_name=data.get("proposal_type_name"),
            team_name=data.get("team_name"),
            owner=data.get("owner"),
            license_of_use=data.get("license_of_use"),
            training=data.get("training"),
            monthly_fee=data.get("monthly_fee"),
            professional_services=data.get("professional_services"),
            monthly_fee_annualized=data.get("monthly_fee_annualized"),
            total_sales=item_sales
        )
        proposals_map[p_id]["items"].append(item_obj)

    return list(proposals_map.values()), errors

# -----------------------------------------------------------------------------
# PHASE 2: ASYNC ORCHESTRATION (IO BOUND)
# -----------------------------------------------------------------------------

async def import_proposals_from_excel(file: UploadFile) -> ImportResponse:
    # 0. Setup Logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(LOGS_DIR, f"import_proposals_{timestamp}.jsonl")
    
    def log_event(event_type: str, message: str, details: Any = None):
        if event_type == "VALIDATION_ERROR": return # Reduce noise for now
        entry = {"timestamp": datetime.now().isoformat(), "event": event_type, "message": message, "details": details}
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except: pass

    log_event("START", f"Starting import: {file.filename}")
    
    try:
        content = await file.read()
        
        # 1. Sync Phase (Pandas)
        # Run in threadpool if extremely large, but for 2k rows direct call is fine.
        # Strict rule: NO DB CALLS HERE.
        proposal_dicts, errors = _parse_excel_sync(content)
        
        log_event("PROGRESS", f"Parsed {len(proposal_dicts)} unique proposals from Excel.")
        
        # 2. Async Phase (DB Persistence)
        upserted_count = 0
        
        for p_data in proposal_dicts:
            try:
                # Convert aggregated total to Decimal128 for Mongo
                p_data["total_value_aggregated"] = Decimal128(p_data["total_value_aggregated"])
                
                # Perform Upsert
                # We use find_one(id).upsert(Set(...)) logic via Beanie
                # logic: Find by ID. If exists, Update. If not, Insert.
                # Actually Beanie `upsert` mechanism with `UpdateOne` is easiest.
                
                p_id = p_data["business_proposal_id"]
                
                # Construct Document (Validate Pydantic)
                # doc = BusinessProposal(**p_data) # This works for Insert, but for Updates we might want to be careful?
                # Actually, replacing the whole document is cleaner for Import (Full Sync).
                # But we need to match the ID.
                
                # Use Repository or Direct Beanie?
                # "Repository.upsert_proposal(p_data)"
                await ProposalRepository.upsert_proposal(p_data)
                upserted_count += 1
                
            except Exception as e:
                errors.append(ImportErrorDetail(
                    line_number=0, 
                    proposal_id=str(p_data.get("business_proposal_id")),
                    message=f"DB Error: {str(e)}"
                ))
                log_event("DB_ERROR", str(e))
        
        log_event("COMPLETE", "Finished", {"upserted": upserted_count, "errors": len(errors)})
        
        return ImportResponse(
            status="completed_with_warnings" if errors else "success",
            summary=ImportSummary(
                total_lines_processed=0, # Hard to track lines vs proposals now
                proposals_upserted=upserted_count,
                details_inserted=0, # Embedded
                customers_updated=0,
                errors_count=len(errors)
            ),
            errors=errors
        )

    except ValueError as e:
        return ImportResponse(status="failed", summary=ImportSummary(total_lines_processed=0, proposals_upserted=0, details_inserted=0, customers_updated=0, errors_count=1), errors=[ImportErrorDetail(line_number=0, message=str(e))])
    except Exception as e:
        return ImportResponse(status="failed", summary=ImportSummary(total_lines_processed=0, proposals_upserted=0, details_inserted=0, customers_updated=0, errors_count=1), errors=[ImportErrorDetail(line_number=0, message=f"Internal: {str(e)}")])


async def get_all_proposals(skip: int = 0, limit: int = 10, filters: Dict[str, Any] = None, sort_by: str = "business_proposal_id", sort_order: int = 1) -> PaginatedResponse:
    # ... (Keep existing logic but point to Repo? logic is already clean enough)
    # Just need to update the DTO mapping since Items are now embedded if we fetch them?
    # This function fetches headers. `BusinessProposal` still has header fields.
    
    query = {}
    if filters:
        if filters.get("id"): query["business_proposal_id"] = filters["id"]
        if filters.get("proposal_name"): query["business_proposal_name"] = {"$regex": filters["proposal_name"], "$options": "i"}
        if filters.get("customer_name"): query["customer_reference"] = {"$regex": filters["customer_name"], "$options": "i"}
        if filters.get("funnel_stage"): query["funnel_percentage"] = {"$in": filters["funnel_stage"]}
        if filters.get("status"): query["business_proposal_status"] = {"$in": filters["status"]}
        if filters.get("search"):
             regex = {"$regex": filters["search"], "$options": "i"}
             query["$or"] = [{"business_proposal_name": regex}, {"customer_reference": regex}]

    sort_mapping = {
        "proposal_id": "business_proposal_id",
        "proposal_name": "business_proposal_name",
        "client_name": "customer_reference",
        "funnel_stage": "funnel_percentage",
        "total_value": "total_value_aggregated",
        "status": "business_proposal_status",
        "created_at": "business_proposal_date",
        "updated_at": "last_status_date"
    }
    db_sort = sort_mapping.get(sort_by, sort_by)
    
    docs, total = await ProposalRepository.fetch_all_paginated(query, db_sort, sort_order, skip, limit)
    
    dtos = [
        ProposalReadDTO(
            proposal_id=str(d.business_proposal_id),
            proposal_name=d.business_proposal_name,
            client_name=d.customer_reference or "N/A",
            funnel_stage=d.funnel_percentage,
            total_value=float(d.total_value_aggregated.to_decimal()) if d.total_value_aggregated else 0.0,
            status=d.business_proposal_status,
            created_at=d.business_proposal_date,
            updated_at=d.last_status_date
        ) for d in docs
    ]
    return PaginatedResponse(items=dtos, total=total)

async def get_proposal_items(proposal_id: int) -> List[ProposalItemDTO]:
    # Fetch Proposal by ID then get items
    proposal = await ProposalRepository.find_by_id(proposal_id)
    if not proposal:
        return []
        
    return [
        ProposalItemDTO(
            id=None, # Embedded items have no specific ID unless we gen one
            product_name=i.product_name,
            type_name=i.proposal_type_name,
            team_name=i.team_name,
            owner=i.owner,
            value=float(i.total_sales) if i.total_sales else 0.0
        ) for i in proposal.items
    ]

async def get_proposals_metadata() -> Dict[str, List[str]]:
    return await ProposalRepository.get_metadata_aggregates()
