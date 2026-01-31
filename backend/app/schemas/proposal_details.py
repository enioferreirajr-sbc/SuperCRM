from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class ProposalDetailsHeaderDTO:
    proposal_id: int
    proposal_name: str | None
    funnel_percentage: str | None
    customer_reference: str | None
    recipient_name: str | None
    recipient_email: str | None
    proposal_status: str | None
    business_proposal_date: date | None
    last_status_date: date | None
    last_note: str | None


@dataclass(frozen=True)
class ProposalDetailsItemDTO:
    product_name: str
    proposal_type_name: str
    team_name: str
    owner: str
    total_sales: Decimal


@dataclass(frozen=True)
class ProposalDetailsDTO:
    proposal: ProposalDetailsHeaderDTO
    items: list[ProposalDetailsItemDTO]
