from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ProposalHeaderDTO:
    proposal_id: int
    proposal_name: str | None
    customer_reference: str | None
    recipient_name: str | None
    recipient_email: str | None
    proposal_status: str | None
    business_proposal_date: date | None
    last_status_date: date | None
    last_note: str | None
