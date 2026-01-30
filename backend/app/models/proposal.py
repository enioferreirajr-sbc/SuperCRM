from sqlalchemy import Date, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    proposal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    closing_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    total_value: Mapped[Numeric | None] = mapped_column(Numeric(18, 2), nullable=True)

    details = relationship("ProposalDetail", back_populates="proposal", cascade="all, delete-orphan")
