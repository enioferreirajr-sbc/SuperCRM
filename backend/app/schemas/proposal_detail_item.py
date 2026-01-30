from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProposalDetailItemDTO:
    product_name: str
    proposal_type_name: str
    team_name: str
    owner: str
    license_of_use: Decimal
    training: Decimal
    monthly_fee: Decimal
    professional_services: Decimal
    monthly_fee_annualized: Decimal
    total_sales: Decimal
