from typing import Optional, Annotated, Any, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, BeforeValidator

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

    @field_validator('business_proposal_date', 'last_status_date', mode='before')
    @classmethod
    def parse_empty_date(cls, v: Any) -> Optional[Any]:
        if isinstance(v, str):
            if not v.strip():
                return None
        return v

    class Config:
        populate_by_name = True
        extra = "ignore" # Ignore extra columns in Excel

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
    id: Optional[str] = None
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
