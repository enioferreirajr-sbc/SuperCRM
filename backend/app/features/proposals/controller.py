from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from app.features.proposals.models import BusinessProposal
from app.features.proposals.schemas import PaginatedResponse, ProposalItemDTO, ImportResponse
from app.features.proposals.service import get_all_proposals, get_proposal_items, import_proposals_from_excel, get_proposals_metadata

router = APIRouter(prefix="/proposals", tags=["Proposals"])

@router.post("/import", response_model=ImportResponse)
async def import_proposals(file: UploadFile = File(...)):
    try:
        result = await import_proposals_from_excel(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return result

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
    return await get_proposals_metadata()
