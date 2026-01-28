from typing import Optional, Annotated, Any, List
from decimal import Decimal
from datetime import datetime
from beanie import Document
from pymongo import ASCENDING, IndexModel
from pydantic import BaseModel, Field, field_validator, BeforeValidator
from bson import Decimal128

def validate_decimal(v: Any) -> Decimal:
    if isinstance(v, Decimal128):
        return v.to_decimal()
    return v

CustomDecimal = Annotated[Decimal, BeforeValidator(validate_decimal)]

def coerce_to_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    return str(v)

CoercedString = Annotated[str, BeforeValidator(coerce_to_str)]

class ProposalImportRow(BaseModel):
    # ... (Keep existing fields, no change needed for ImportRow as it takes from Pandas/Dict usually)
    business_proposal_id: int = Field(alias="Business Proposal ID")
    product_name: str = Field(alias="Product Name")
    main_contract_id: Optional[int] = Field(default=None, alias="Main Contract ID")
    customer_reference: Optional[str] = Field(default=None, alias="Customer Reference")
    business_proposal_date: Optional[datetime] = Field(default=None, alias="Business Proposal Date")
    last_status_date: Optional[datetime] = Field(default=None, alias="Last Status Date")
    funnel_percentage: Optional[str] = Field(default=None, alias="Funnel Percentage")
    license_of_use: Optional[Decimal] = Field(default=None, alias="R$ License of Use")
    training: Optional[Decimal] = Field(default=None, alias="R$ Training")
    monthly_fee: Optional[Decimal] = Field(default=None, alias="R$ Monthly Fee")
    professional_services: Optional[Decimal] = Field(default=None, alias="R$ Professional Services")
    monthly_fee_annualized: Optional[Decimal] = Field(default=None, alias="Monthly Fee (Annualized)")
    total_sales: Optional[Decimal] = Field(default=None, alias="R$ Total Sales")
    last_note: Optional[str] = Field(default=None, alias="Last Note")
    proposal_type_name: Optional[str] = Field(default=None, alias="Proposal Type Name")
    team_name: Optional[str] = Field(default=None, alias="Team Name")
    owner: Optional[str] = Field(default=None, alias="Owner")
    business_proposal_name: Optional[str] = Field(default=None, alias="Business Proposal Name")
    recipient_name: Optional[str] = Field(default=None, alias="Recipient Name")
    recipient_e_mail: Optional[str] = Field(default=None, alias="Recipient E-mail")
    business_proposal_status: Optional[str] = Field(default=None, alias="Business Proposal Status")
    funnel_percentage_id: Optional[CoercedString] = Field(default=None, alias="Funnel Percentage ID")
    aging_business_proposal: Optional[CoercedString] = Field(default=None, alias="Aging Business Proposal")
    aging_status: Optional[str] = Field(default=None, alias="Aging Status")

    class Config:
        populate_by_name = True
        extra = "ignore" # Ignore extra columns in Excel

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
    aging_business_proposal: Optional[str] = None
    aging_status: Optional[str] = None

    class Settings:
        name = "business_proposals"
        indexes = [
            IndexModel([("business_proposal_id", ASCENDING)], unique=True)
        ]

class BusinessProposalItem(Document):
    linked_proposal_id: int
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

    class Settings:
        name = "business_proposal_items"
        indexes = [
            IndexModel([("linked_proposal_id", ASCENDING)])
        ]

class ProposalReadDTO(BaseModel):
    proposal_id: str
    proposal_name: Optional[str] = None
    client_name: Optional[str] = None
    # product_name removed for consolidated view
    funnel_stage: Optional[str] = None
    total_value: Optional[float] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProposalItemDTO(BaseModel):
    id: Optional[str] = None # Mongo ID
    product_name: str
    type_name: Optional[str] = None
    team_name: Optional[str] = None
    owner: Optional[str] = None
    value: Optional[float] = None # total_sales
    
class PaginatedResponse(BaseModel):
    items: list[ProposalReadDTO]
    total: int

class ImportSummary(BaseModel):
    total_lines_processed: int
    proposals_upserted: int
    details_inserted: int
    customers_updated: int
    errors_count: int

class ImportErrorDetail(BaseModel):
    line_number: int
    proposal_id: Optional[str] = None
    column: Optional[str] = None
    message: str
    value_provided: Optional[Any] = None

class ImportResponse(BaseModel):
    status: str
    summary: ImportSummary
    errors: List[ImportErrorDetail]
