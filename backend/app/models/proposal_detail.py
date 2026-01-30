from sqlalchemy import ForeignKey, Integer, Numeric, text
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProposalDetail(Base):
    __tablename__ = "proposal_detail"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[int] = mapped_column(
        ForeignKey("proposal.proposal_id"), nullable=False
    )

    proposal_type_name: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False)
    product_name: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False)
    team_name: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False)
    owner: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False)

    license_of_use: Mapped[Numeric] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    training: Mapped[Numeric] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    monthly_fee: Mapped[Numeric] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    professional_services: Mapped[Numeric] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    monthly_fee_annualized: Mapped[Numeric] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    total_sales: Mapped[Numeric] = mapped_column(Numeric(18, 2), nullable=False)

    proposal = relationship("Proposal", back_populates="details")
