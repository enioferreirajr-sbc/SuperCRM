from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProposalGridDTO:
    proposal_id: int
    customer_reference: str | None
    proposal_name: str | None
    funnel_percentage: str
    total_value: Decimal
