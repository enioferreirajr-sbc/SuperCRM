from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Integer, Index, UniqueConstraint, text
from sqlalchemy.dialects.mssql import DATETIME2, NVARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ImportMapping(Base):
    __tablename__ = "import_mappings"
    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_import_mappings_name_version"),
        Index("ix_import_mappings_name_is_active", "name", "is_active"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(NVARCHAR(120), nullable=False)
    version: Mapped[str] = mapped_column(NVARCHAR(50), nullable=False)
    mapping_json: Mapped[str] = mapped_column(NVARCHAR(None), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        DATETIME2(), nullable=False, server_default=text("GETDATE()")
    )
