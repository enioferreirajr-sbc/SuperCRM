from typing import List, Dict, Any, Tuple, Optional
from app.features.proposals.models import Proposal
from pymongo import UpdateOne, InsertOne
from pymongo.client_session import ClientSession
from pymongo.client_session import ClientSession

class ProposalRepository:
    
    @staticmethod
    async def fetch_all_paginated(
        query: Dict[str, Any], 
        sort_field: str, 
        sort_order: int, 
        skip: int, 
        limit: int
    ) -> Tuple[List[Proposal], int]:
        """
        Fetches proposals with pagination, sorting, and filtering.
        Returns (items, total_count).
        """
        # Count total documents matching query
        total_count = await Proposal.find(query).count()
        
        # Fetch page
        cursor = Proposal.find(query).sort((sort_field, sort_order)).skip(skip).limit(limit)
        items = await cursor.to_list()
        
        return items, total_count

    # @staticmethod
    # async def fetch_items_by_proposal_id(proposal_id: int) -> List[ProposalItem]:
    #    """
    #    Fetches all items linked to a specific proposal ID.
    #    """
    #    return await ProposalItem.find({"linked_proposal_id": proposal_id}).to_list()

    @staticmethod
    async def get_metadata_aggregates() -> Dict[str, List[str]]:
        """
        Uses native MongoDB Aggregation/Distinct to get unique values for filters.
        Optimized for performance.
        """
        # 1. Statuses (from Header)
        statuses = await Proposal.find_all().distinct("business_proposal_status")
        
        # 2. Funnel Stages (from Header)
        funnels = await Proposal.find_all().distinct("funnel_percentage")
        
        # 3. Products (from Items)
        # Embedded query: "items.product_name"
        products = await Proposal.find_all().distinct("items.product_name")
        
        return {
            "products": sorted([p for p in products if p]),
            "statuses": sorted([s for s in statuses if s]),
            "funnel_stages": sorted([f for f in funnels if f])
        }

    @staticmethod
    async def upsert_proposal(data: Dict[str, Any]):
        """
        Upserts a full proposal document including embedded items.
        Using high-level Beanie API to avoid get_motor_collection issues.
        """
        p_id = data.get("business_proposal_id")
        if not p_id: raise ValueError("Missing Proposal ID")
        
        # 1. Try to find existing
        existing_doc = await Proposal.find_one(Proposal.business_proposal_id == p_id)
        
        if existing_doc:
            # 2. Update existing
            # We want to replace fields. `set` takes a dict in recent Beanie versions or we iterate.
            # Using model_copy(update=data) is Pydantic v2 style, checking Beanie support.
            # Safer: Manually update fields or use .set() with dictionary
            
            # Note: For strict replacement of 'items' and other fields, passing dict to .item() or similar?
            # Simplest: Update attributes and save.
            for key, value in data.items():
                if hasattr(existing_doc, key):
                     setattr(existing_doc, key, value)
            
            await existing_doc.save()
        else:
            # 3. Insert new
            new_doc = Proposal(**data)
            await new_doc.insert()

    @staticmethod
    async def find_by_id(proposal_id: int) -> Optional[Proposal]:
        return await Proposal.find_one({"business_proposal_id": proposal_id})
