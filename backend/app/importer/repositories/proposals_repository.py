from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import delete, select

from app.core.import_context import ImportContext
from app.models.proposal import Proposal
from app.models.proposal_detail import ProposalDetail


def import_proposals(ctx: ImportContext) -> None:
    for proposal_id, proposal_data in ctx.proposals.items():
        proposal = (
            ctx.session.execute(
                select(Proposal).where(Proposal.proposal_id == proposal_id)
            )
            .scalars()
            .first()
        )
        if proposal is None:
            proposal = Proposal(proposal_id=proposal_id)
            ctx.session.add(proposal)

        for field_name, value in proposal_data.items():
            if field_name == "proposal_id":
                continue
            setattr(proposal, field_name, value)


def import_proposal_details(ctx: ImportContext) -> None:
    if not ctx.proposals:
        return

    proposal_ids = list(ctx.proposals.keys())
    ctx.session.execute(
        delete(ProposalDetail).where(ProposalDetail.proposal_id.in_(proposal_ids))
    )

    details_by_proposal: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for detail in ctx.proposal_details:
        proposal_id = detail.get("proposal_id")
        if proposal_id is None:
            continue
        details_by_proposal[int(proposal_id)].append(detail)

    for proposal_id, details in details_by_proposal.items():
        for detail in details:
            detail_payload = dict(detail)
            detail_payload.pop("proposal_id", None)
            ctx.session.add(
                ProposalDetail(
                    proposal_id=proposal_id,
                    **detail_payload,
                )
            )
