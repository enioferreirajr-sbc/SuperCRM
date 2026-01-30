from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Owner(Base):
    __tablename__ = "owner"
    __table_args__ = (UniqueConstraint("owner_name", name="uq_owner_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_name: Mapped[str] = mapped_column(String(150), nullable=False)
