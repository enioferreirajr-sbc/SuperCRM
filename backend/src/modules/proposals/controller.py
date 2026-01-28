from fastapi import APIRouter, UploadFile, File, HTTPException
from src.modules.proposals.service import import_proposals_from_excel

router = APIRouter(prefix="/proposals", tags=["Proposals"])

from src.modules.proposals.models import BusinessProposal, PaginatedResponse, ProposalItemDTO, ImportResponse
from src.modules.proposals.service import get_all_proposals, get_proposal_items, import_proposals_from_excel

@router.post("/import", response_model=ImportResponse)
async def import_proposals(file: UploadFile = File(...)):
    # Validate extension
    if not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Invalid file extension. Please upload a .xlsx file.")
    
    # Validate content type (soft check, dependent on client)
    valid_types = [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream" # Sometimes sends as octet-stream
    ]
    if file.content_type not in valid_types:
         # Optional: Log warning, but maybe enforce strictly as per requirements
         # Requirement: MIME Type inválido (deve ser application/vnd...)
         pass 

    if file.content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
         # Let's enforce strictly if that's the requirement, but check if we should allow generic octet-stream fallback
         # "MIME Type inválido (deve ser `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)"
         # We will be strict.
         raise HTTPException(status_code=400, detail="Invalid MIME type. Expected application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    result = await import_proposals_from_excel(file)
    
    if result["status"] == "error":
         raise HTTPException(status_code=500, detail=result["message"])
         
    if result["status"] == "error":
         raise HTTPException(status_code=500, detail=result["message"])
         
    return result

from typing import List, Optional
from fastapi import Query
from src.modules.proposals.models import BusinessProposal, PaginatedResponse, ProposalItemDTO
from src.modules.proposals.service import get_all_proposals, get_proposal_items

@router.get("/{id}/items", response_model=List[ProposalItemDTO])
async def get_items(id: int):
    return await get_proposal_items(proposal_id=id)

@router.get("/", response_model=PaginatedResponse)
async def get_proposals(
    skip: int = 0, 
    limit: int = 20,
    id: Optional[int] = None,
    proposal_name: Optional[str] = None,
    customer_name: Optional[str] = None,
    product: Optional[List[str]] = Query(None),
    funnel_stage: Optional[List[str]] = Query(None),
    status: Optional[List[str]] = Query(None),
    amount_min: Optional[float] = None,
    amount_max: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "business_proposal_id",
    sort_order: Optional[str] = "asc"
):
    filters = {}
    if search: filters["search"] = search
    if id is not None: filters["id"] = id
    if proposal_name: filters["proposal_name"] = proposal_name
    if customer_name: filters["customer_name"] = customer_name
    if product: filters["product"] = product
    if funnel_stage: filters["funnel_stage"] = funnel_stage
    if status: filters["status"] = status
    if amount_min is not None: filters["amount_min"] = amount_min
    if amount_max is not None: filters["amount_max"] = amount_max

    mongo_sort_order = 1 if sort_order == "asc" else -1
    
    return await get_all_proposals(
        skip=skip, 
        limit=limit, 
        filters=filters,
        sort_by=sort_by,
        sort_order=mongo_sort_order
    )

@router.get("/metadata")
async def get_metadata():
    from src.modules.proposals.service import get_proposals_metadata
    return await get_proposals_metadata()
