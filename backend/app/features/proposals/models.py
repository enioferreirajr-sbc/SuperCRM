from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime
from beanie import Document, DecimalAnnotation
from pydantic import BaseModel, Field

class ProposalItem(BaseModel):
    product_name: Optional[str] = None
    proposal_type_name: Optional[str] = None
    team_name: Optional[str] = None
    owner: Optional[str] = None
    license_of_use: Optional[DecimalAnnotation] = None
    training: Optional[DecimalAnnotation] = None
    monthly_fee: Optional[DecimalAnnotation] = None
    professional_services: Optional[DecimalAnnotation] = None
    monthly_fee_annualized: Optional[DecimalAnnotation] = None
    total_sales: Optional[DecimalAnnotation] = None

class Proposal(Document):
    business_proposal_id: int # ID Externo
    main_contract_id: Optional[int] = None
    customer_reference: Optional[str] = None
    business_proposal_date: Optional[date] = None
    last_status_date: Optional[date] = None
    funnel_percentage: Optional[str] = None
    last_note: Optional[str] = None
    business_proposal_name: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    business_proposal_status: Optional[str] = None
    aging_business_proposal: Optional[str] = None
    aging_status: Optional[str] = None
    
    total_value_aggregated: Optional[DecimalAnnotation] = None # Computed Field
    
    # Array de Itens (Embedded)
    items: List[ProposalItem] = Field(default_factory=list)

    class Settings:
        name = "proposals"
        indexes = [
            "business_proposal_id",
            "main_contract_id"
        ]

