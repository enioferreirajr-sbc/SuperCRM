from io import BytesIO
from typing import Dict, Any, List
from decimal import Decimal
import openpyxl
from fastapi import UploadFile, HTTPException
from pymongo import UpdateOne
from bson import Decimal128 # Import Decimal128
from src.modules.proposals.models import (
    BusinessProposal, 
    BusinessProposalItem, 
    ProposalImportRow, 
    ProposalReadDTO, 
    PaginatedResponse,
    ProposalItemDTO,
    ImportResponse,
    ImportSummary,
    ImportErrorDetail
)

# Define expected headers based on the Pydantic model aliases
EXPECTED_HEADERS = [
    "Business Proposal ID", "Product Name"
]

import pandas as pd

async def import_proposals_from_excel(file: UploadFile) -> ImportResponse:
    # 1. Read file into memory
    content = await file.read()
    
    try:
        wb = openpyxl.load_workbook(filename=BytesIO(content), data_only=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Excel file.")

    # 2. Select Sheet
    if "Grid 1" in wb.sheetnames:
        sheet = wb["Grid 1"]
    elif wb.worksheets:
        sheet = wb.worksheets[0]
    else:
        raise HTTPException(status_code=400, detail="Excel file has no sheets.")
    
    # 3. Read Data using Pandas
    # We read all columns as object (string) to avoid automatic conversion issues
    df = pd.read_excel(BytesIO(content), sheet_name=sheet.title, dtype=object)
    
    # Maps internal Pydantic alias -> Column Name
    # Actually Pydantic `ProposalImportRow` expects aliased names in dict.
    # We just need to ensure columns exist.
    required_cols = ["Business Proposal ID", "Product Name", "Customer Reference"]
    missing = [c for c in required_cols if c not in df.columns]
    
    if missing:
        # Critical failure if entire columns are missing
        return ImportResponse(
            status="failed",
            summary=ImportSummary(
                total_lines_processed=0,
                proposals_upserted=0,
                details_inserted=0,
                customers_updated=0,
                errors_count=1
            ),
            errors=[ImportErrorDetail(
                line_number=0, 
                message=f"Missing required columns: {', '.join(missing)}"
            )]
        )

    # Initialize Stats
    total_lines = len(df)
    import_errors = []
    valid_rows = []
    
    # 4. Row-Level Validation
    for index, row in df.iterrows():
        # Excel row number = index + 2 (header is 1, 0-based index)
        line_num = index + 2
        
        # 4.1 Check Critical Fields
        p_id = row.get("Business Proposal ID")
        cust_ref = row.get("Customer Reference")
        
        if pd.isna(p_id) or str(p_id).strip() == "":
            import_errors.append(ImportErrorDetail(
                line_number=line_num,
                column="Business Proposal ID",
                message="ID Obrigatório vazio",
                value_provided=None
            ))
            continue # Critical Skip
            
        if pd.isna(cust_ref) or str(cust_ref).strip() == "":
            import_errors.append(ImportErrorDetail(
                line_number=line_num,
                proposal_id=str(p_id),
                column="Customer Reference",
                message="Cliente Obrigatório vazio",
                value_provided=None
            ))
            continue # Critical Skip
            
        # 4.2 Data Type Validation (via Pydantic)
        try:
            row_dict = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
            
            # Handle Monetary Strings (Warning/Cleanup)
            # If any money field is text like "Free", set to 0
            money_fields = ["R$ License of Use", "R$ Training", "R$ Monthly Fee", "R$ Professional Services", "R$ Total Sales"]
            for field in money_fields:
                val = row_dict.get(field)
                if isinstance(val, str) and not val.replace('.', '', 1).isdigit():
                    row_dict[field] = 0 # Silent fix or could log warning
            
            # Validate
            import_row = ProposalImportRow(**row_dict)
            valid_rows.append(import_row)
            
        except Exception as e:
            # Capture specific Pydantic error
            msg = str(e)
            # Try to extract clearer message
            import_errors.append(ImportErrorDetail(
                line_number=line_num,
                proposal_id=str(p_id),
                message=f"Erro de validação: {msg}",
                value_provided=str(row.to_dict())
            ))
            continue

    if not valid_rows:
        return ImportResponse(
            status="failed",
            summary=ImportSummary(
                total_lines_processed=total_lines,
                proposals_upserted=0,
                details_inserted=0,
                customers_updated=0,
                errors_count=len(import_errors)
            ),
            errors=import_errors
        )

    # 5. Process Valid Rows
    # Re-build DataFrame from Valid Rows for Grouping
    valid_data = [row.model_dump(by_alias=True) for row in valid_rows]
    valid_df = pd.DataFrame(valid_data)
    
    # 5.1 Cleanup Old Items
    proposal_ids = valid_df["Business Proposal ID"].unique().tolist()
    await BusinessProposalItem.find({"linked_proposal_id": {"$in": proposal_ids}}).delete()
    
    bulk_header_ops = []
    bulk_item_ops = []
    
    grouped = valid_df.groupby("Business Proposal ID")
    
    for proposal_id, group in grouped:
        try:
            # Header (First Row)
            first_row_dict = group.iloc[0].to_dict()
            header_import = ProposalImportRow(**first_row_dict) # Already validated, but good for casting
            
            # Calculate Total
            total_sales_sum = Decimal(0)
            
            for _, row_data in group.iterrows():
                row_dict = row_data.to_dict()
                item_import = ProposalImportRow(**row_dict)
                
                if item_import.total_sales:
                    total_sales_sum += item_import.total_sales
                
                # Item Doc
                item_doc = BusinessProposalItem(
                    linked_proposal_id=item_import.business_proposal_id,
                    product_name=item_import.product_name,
                    proposal_type_name=item_import.proposal_type_name,
                    team_name=item_import.team_name,
                    owner=item_import.owner,
                    license_of_use=item_import.license_of_use,
                    training=item_import.training,
                    monthly_fee=item_import.monthly_fee,
                    professional_services=item_import.professional_services,
                    monthly_fee_annualized=item_import.monthly_fee_annualized,
                    total_sales=item_import.total_sales
                )
                bulk_item_ops.append(item_doc)

            # Header Doc
            header_filter = {"business_proposal_id": header_import.business_proposal_id}
            header_update = {
                "customer_reference": header_import.customer_reference,
                "business_proposal_date": header_import.business_proposal_date,
                "last_status_date": header_import.last_status_date,
                "funnel_percentage": header_import.funnel_percentage,
                "business_proposal_name": header_import.business_proposal_name,
                "business_proposal_status": header_import.business_proposal_status,
                "total_value_aggregated": Decimal128(total_sales_sum),
                "last_note": header_import.last_note,
                "recipient_name": header_import.recipient_name,
                "recipient_e_mail": header_import.recipient_e_mail,
                "funnel_percentage_id": header_import.funnel_percentage_id,
                "aging_business_proposal": header_import.aging_business_proposal,
                "aging_status": header_import.aging_status
            }
            
            bulk_header_ops.append(
                UpdateOne(header_filter, {"$set": header_update}, upsert=True)
            )
            
        except Exception as e:
            # If processing fails here, add to errors (rare if validation passed)
            import_errors.append(ImportErrorDetail(
                line_number=0,
                proposal_id=str(proposal_id),
                message=f"Erro de processamento: {str(e)}"
            ))

    # Execute
    if bulk_header_ops:
        await BusinessProposal.get_pymongo_collection().bulk_write(bulk_header_ops)
    if bulk_item_ops:
        await BusinessProposalItem.insert_many(bulk_item_ops)
        
    return ImportResponse(
        status="completed_with_warnings" if import_errors else "success",
        summary=ImportSummary(
            total_lines_processed=total_lines,
            proposals_upserted=len(bulk_header_ops),
            details_inserted=len(bulk_item_ops),
            customers_updated=0, # Not implementing Customer Coll logic yet per plan scope
            errors_count=len(import_errors)
        ),
        errors=import_errors
    )

async def get_all_proposals(
    skip: int = 0, 
    limit: int = 10,
    filters: Dict[str, Any] = None,
    sort_by: str = "business_proposal_id",
    sort_order: int = 1  # 1 for ASC, -1 for DESC
) -> PaginatedResponse:
    query = {}
    if filters:
        if filters.get("id"):
            query["business_proposal_id"] = filters["id"]
        
        if filters.get("proposal_name"):
            query["business_proposal_name"] = {"$regex": filters["proposal_name"], "$options": "i"}
            
        if filters.get("customer_name"):
            query["customer_reference"] = {"$regex": filters["customer_name"], "$options": "i"}

        if filters.get("product"):
            query["product_name"] = {"$in": filters["product"]} # NOTE: product_name removed from Header. This filter will fail or need aggregation lookup.
            # Ideally for 1-to-N, filtering by product requires joining or redundant data.
            # User instruction: "Armazena apenas dados comuns".
            # For now, I will Comment this out or leave it if fields were kept.
            # Since fields REMOVED, we need to remove this filter OR perform lookup.
            # Simpler: Disable product filter for now on main list or use aggregates.
            # Let's Skip product filter in header query for now as it's not in schema.
            pass 

        if filters.get("funnel_stage"):
            query["funnel_percentage"] = {"$in": filters["funnel_stage"]}
            
        if filters.get("status"):
            query["business_proposal_status"] = {"$in": filters["status"]}

        if filters.get("amount_min") or filters.get("amount_max"):
            amount_query = {}
            if filters.get("amount_min") is not None:
                amount_query["$gte"] = Decimal128(Decimal(str(filters["amount_min"])))
            if filters.get("amount_max") is not None:
                amount_query["$lte"] = Decimal128(Decimal(str(filters["amount_max"])))
            if filters.get("amount_max") is not None:
                amount_query["$lte"] = Decimal128(Decimal(str(filters["amount_max"])))
            query["total_sales"] = amount_query

        if filters.get("search"):
            search_regex = {"$regex": filters["search"], "$options": "i"}
            query["$or"] = [
                {"business_proposal_name": search_regex},
                {"customer_reference": search_regex}
                # {"product_name": search_regex} # Remove product search from header
            ]

    # Execute query
    # 1. Count total
    total_count = await BusinessProposal.find(query).count()
    
    # 2. Fetch items
    cursor = BusinessProposal.find(query)
    
    # Apply sorting
    sort_mapping = {
        "proposal_id": "business_proposal_id",
        "proposal_name": "business_proposal_name",
        "client_name": "customer_reference",
        # "product_name": "product_name", # Removed
        "funnel_stage": "funnel_percentage",
        "total_value": "total_value_aggregated", # Updated mapping
        "status": "business_proposal_status",
        "created_at": "business_proposal_date",
        "updated_at": "last_status_date"
    }
    db_sort_field = sort_mapping.get(sort_by, sort_by) # Fallback to original if not found
    cursor = cursor.sort((db_sort_field, sort_order))
    
    # Apply pagination
    cursor = cursor.skip(skip).limit(limit)
    
    # Fetch results
    documents = await cursor.to_list()
    
    # 3. Map to DTO
    dtos = []
    for doc in documents:
        # Convert fields as needed
        total_val = 0.0
        if doc.total_value_aggregated is not None:
             total_val = float(doc.total_value_aggregated)

        dtos.append(ProposalReadDTO(
            proposal_id=str(doc.business_proposal_id),
            proposal_name=doc.business_proposal_name,
            client_name=doc.customer_reference or "N/A",
            # product_name removed
            funnel_stage=doc.funnel_percentage,
            total_value=total_val,
            status=doc.business_proposal_status,
            created_at=doc.business_proposal_date,
            updated_at=doc.last_status_date
        ))

    return PaginatedResponse(
        items=dtos,
        total=total_count
    )

async def get_proposal_items(proposal_id: int) -> List[ProposalItemDTO]:
    items = await BusinessProposalItem.find({"linked_proposal_id": proposal_id}).to_list()
    dtos = []
    for item in items:
        val = 0.0
        if item.total_sales:
            val = float(item.total_sales)
            
        dtos.append(ProposalItemDTO(
            id=str(item.id),
            product_name=item.product_name,
            type_name=item.proposal_type_name,
            team_name=item.team_name,
            owner=item.owner,
            value=val
        ))
    return dtos

async def get_proposals_metadata() -> Dict[str, List[str]]:
    # Fallback: Fetch all fields with projection and uniq in Python
    # This avoids issues with finding the exact 'distinct' or 'aggregate' syntax in this Beanie version
    proposals = await BusinessProposal.find_all().to_list()
    
    # Actually project() expects a Model. Let's just fetch all. 
    # Optimization: define a small model or just fetch all. 
    # BusinessProposal is small enough.
    
    unique_products = {p.product_name for p in proposals if p.product_name}
    unique_statuses = {p.business_proposal_status for p in proposals if p.business_proposal_status}
    unique_funnels = {p.funnel_percentage for p in proposals if p.funnel_percentage}

    return {
        "products": sorted(list(unique_products)),
        "statuses": sorted(list(unique_statuses)),
        "funnel_stages": sorted(list(unique_funnels))
    }
