from typing import Optional, Annotated, Any
from decimal import Decimal
from datetime import datetime
from beanie import Document
from pymongo import ASCENDING, IndexModel
from pydantic import BaseModel, BeforeValidator
from bson import Decimal128

def validate_decimal(v: Any) -> Decimal:
    if isinstance(v, Decimal128):
        return v.to_decimal()
    return v

CustomDecimal = Annotated[Decimal, BeforeValidator(validate_decimal)]

class BusinessProposal(Document):
    business_proposal_id: int
    customer_reference: Optional[str] = None
    business_proposal_date: Optional[datetime] = None
    last_status_date: Optional[datetime] = None
    funnel_percentage: Optional[str] = None
    business_proposal_name: Optional[str] = None
    business_proposal_status: Optional[str] = None
    total_value_aggregated: Optional[CustomDecimal] = None # Aggregated Total
    last_note: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_e_mail: Optional[str] = None
    funnel_percentage_id: Optional[str] = None
    aging_status: Optional[str] = None
    
    # Embedded Items
    items: list["ProposalItem"] = []

    class Settings:
        name = "business_proposals"
        indexes = [
            IndexModel([("business_proposal_id", ASCENDING)], unique=True)
        ]

class ProposalItem(BaseModel):
    product_name: str
    proposal_type_name: Optional[str] = None
    team_name: Optional[str] = None
    owner: Optional[str] = None
    
    # Financials (Item Level)
    license_of_use: Optional[CustomDecimal] = None
    training: Optional[CustomDecimal] = None
    monthly_fee: Optional[CustomDecimal] = None
    professional_services: Optional[CustomDecimal] = None
    monthly_fee_annualized: Optional[CustomDecimal] = None
    total_sales: Optional[CustomDecimal] = None
