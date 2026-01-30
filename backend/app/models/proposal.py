from sqlalchemy import Date, Integer
from sqlalchemy.dialects.mssql import NVARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Proposal(Base):
    __tablename__ = "proposal"

    proposal_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    main_contract_id: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_reference: Mapped[str | None] = mapped_column(NVARCHAR(255), nullable=True)
    proposal_name: Mapped[str | None] = mapped_column(NVARCHAR(255), nullable=True)
    recipient_name: Mapped[str | None] = mapped_column(NVARCHAR(255), nullable=True)
    recipient_email: Mapped[str | None] = mapped_column(NVARCHAR(255), nullable=True)
    proposal_status: Mapped[str | None] = mapped_column(NVARCHAR(255), nullable=True)
    business_proposal_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    last_status_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    funnel_percentage: Mapped[str] = mapped_column(NVARCHAR(100), nullable=False)
    last_note: Mapped[str | None] = mapped_column(NVARCHAR(4000), nullable=True)

    details = relationship("ProposalDetail", back_populates="proposal", cascade="all, delete-orphan")
