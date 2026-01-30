from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProposalDetail(Base):
    __tablename__ = "proposal_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[int] = mapped_column(ForeignKey("proposals.id"), nullable=False)

    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    team_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    value: Mapped[Numeric | None] = mapped_column(Numeric(18, 2), nullable=True)

    proposal = relationship("Proposal", back_populates="details")
