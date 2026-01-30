from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Customer(Base):
    __tablename__ = "customer"

    main_contract_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
