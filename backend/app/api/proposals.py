from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.proposal import Proposal
from app.models.proposal_detail import ProposalDetail
from app.schemas.proposal_grid import ProposalGridDTO
from app.schemas.proposal_header import ProposalHeaderDTO
from app.schemas.proposal_detail_item import ProposalDetailItemDTO
from app.schemas.proposal_details import (
    ProposalDetailsDTO,
    ProposalDetailsHeaderDTO,
    ProposalDetailsItemDTO,
)

router = APIRouter(prefix="/api/v1", tags=["proposals"])


@router.get("/proposals")
def list_proposals(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_db),
):
    total = session.execute(select(func.count()).select_from(Proposal)).scalar_one()

    total_value_subquery = (
        select(
            ProposalDetail.proposal_id.label("proposal_id"),
            func.coalesce(func.sum(ProposalDetail.total_sales), 0).label("total_value"),
        )
        .group_by(ProposalDetail.proposal_id)
        .subquery()
    )

    stmt = (
        select(
            Proposal.proposal_id,
            Proposal.customer_reference,
            Proposal.proposal_name,
            Proposal.funnel_percentage,
            func.coalesce(total_value_subquery.c.total_value, 0).label("total_value"),
        )
        .select_from(Proposal)
        .outerjoin(total_value_subquery, Proposal.proposal_id == total_value_subquery.c.proposal_id)
        .order_by(Proposal.proposal_id)
        .offset(skip)
        .limit(limit)
    )

    rows = session.execute(stmt).all()
    items = [
        ProposalGridDTO(
            proposal_id=row.proposal_id,
            customer_reference=row.customer_reference,
            proposal_name=row.proposal_name,
            funnel_percentage=row.funnel_percentage,
            total_value=row.total_value,
        )
        for row in rows
    ]

    return {"items": [asdict(item) for item in items], "total": total}


@router.get("/proposals/{proposal_id}")
def get_proposal_header(
    proposal_id: int,
    session: Session = Depends(get_db),
):
    proposal = (
        session.execute(select(Proposal).where(Proposal.proposal_id == proposal_id))
        .scalars()
        .first()
    )
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found.")

    header = ProposalHeaderDTO(
        proposal_id=proposal.proposal_id,
        proposal_name=proposal.proposal_name,
        customer_reference=proposal.customer_reference,
        recipient_name=proposal.recipient_name,
        recipient_email=proposal.recipient_email,
        proposal_status=proposal.proposal_status,
        business_proposal_date=proposal.business_proposal_date,
        last_status_date=proposal.last_status_date,
        last_note=proposal.last_note,
    )
    return asdict(header)


@router.get("/proposals/{proposal_id}/details")
def get_proposal_details(
    proposal_id: int,
    session: Session = Depends(get_db),
):
    proposal = (
        session.execute(select(Proposal).where(Proposal.proposal_id == proposal_id))
        .scalars()
        .first()
    )
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found.")

    items = (
        session.execute(
            select(ProposalDetail).where(ProposalDetail.proposal_id == proposal_id)
        )
        .scalars()
        .all()
    )

    header = ProposalDetailsHeaderDTO(
        proposal_id=proposal.proposal_id,
        proposal_name=proposal.proposal_name,
        funnel_percentage=proposal.funnel_percentage,
        customer_reference=proposal.customer_reference,
        recipient_name=proposal.recipient_name,
        recipient_email=proposal.recipient_email,
        proposal_status=proposal.proposal_status,
        business_proposal_date=proposal.business_proposal_date,
        last_status_date=proposal.last_status_date,
        last_note=proposal.last_note,
    )

    detail_items = [
        ProposalDetailsItemDTO(
            product_name=item.product_name,
            proposal_type_name=item.proposal_type_name,
            team_name=item.team_name,
            owner=item.owner,
            total_sales=item.total_sales,
        )
        for item in items
    ]

    details = ProposalDetailsDTO(
        proposal=header,
        items=detail_items,
    )
    return asdict(details)


@router.get("/proposals/{proposal_id}/items")
def get_proposal_items(
    proposal_id: int,
    session: Session = Depends(get_db),
):
    items = (
        session.execute(
            select(ProposalDetail).where(ProposalDetail.proposal_id == proposal_id)
        )
        .scalars()
        .all()
    )

    result = [
        ProposalDetailItemDTO(
            product_name=item.product_name,
            proposal_type_name=item.proposal_type_name,
            team_name=item.team_name,
            owner=item.owner,
            license_of_use=item.license_of_use,
            training=item.training,
            monthly_fee=item.monthly_fee,
            professional_services=item.professional_services,
            monthly_fee_annualized=item.monthly_fee_annualized,
            total_sales=item.total_sales,
        )
        for item in items
    ]

    return [asdict(item) for item in result]
