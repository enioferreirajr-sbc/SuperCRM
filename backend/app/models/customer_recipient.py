from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CustomerRecipient(Base):
    __tablename__ = "customer_recipient"
    __table_args__ = (
        UniqueConstraint("main_contract_id", "recipient_email", name="uq_customer_recipient_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    main_contract_id: Mapped[int] = mapped_column(
        ForeignKey("customer.main_contract_id"), nullable=False
    )
    recipient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    cellphone: Mapped[str | None] = mapped_column(String(50), nullable=True)
