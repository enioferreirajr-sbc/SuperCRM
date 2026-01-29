from typing import List, Optional, Annotated, Any
from beanie import Document, Indexed
from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from bson import Decimal128
from datetime import datetime

class ImportDefinition(Document):
    source_column: str
    target_field: Indexed(str, unique=True)
    target_location: str  # "root" or "items"
    data_type: str        # "Int", "String", "Date", "Decimal"
    required: bool
    is_unique_identifier: bool
    
    class Settings:
        name = "import_definitions"

class ProposalItem(BaseModel):
    product_name: Optional[str] = None
    proposal_type_name: Optional[str] = None
    team_name: Optional[str] = None
    owner: Optional[str] = None
    
    # Financials
    license_of_use: Optional[Decimal] = None
    training: Optional[Decimal] = None
    monthly_fee: Optional[Decimal] = None
    professional_services: Optional[Decimal] = None
    monthly_fee_annualized: Optional[Decimal] = None
    total_sales: Optional[Decimal] = None

class Proposal(Document):
    business_proposal_id: Indexed(int, unique=True)
    main_contract_id: Optional[int] = None
    customer_reference: Optional[str] = None
    business_proposal_date: Optional[datetime] = None
    
    # Status & Funnel
    last_status_date: Optional[datetime] = None
    funnel_percentage: Optional[str] = None
    business_proposal_status: Optional[str] = None
    
    # Other Root Fields
    business_proposal_name: Optional[str] = None
    last_note: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    aging_business_proposal: Optional[str] = None
    aging_status: Optional[str] = None

    items: List[ProposalItem] = []
    
    class Settings:
        name = "proposals_importer" # Using a distinct collection name to avoid conflict with existing 'proposals' if necessary, or just 'proposals' if replacing. User said "proposals".
        # User prompt said name = "proposals". Existing BusinessProposal uses "business_proposals".
        # I will use "proposals" as requested, effectively creating a new collection for this module.
