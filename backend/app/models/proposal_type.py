from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProposalType(Base):
    __tablename__ = "proposal_type"
    __table_args__ = (UniqueConstraint("proposal_type_name", name="uq_proposal_type_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_type_name: Mapped[str] = mapped_column(String(150), nullable=False)
