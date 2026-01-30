"""Create import_mappings table

Revision ID: 0002_import_mappings
Revises: 0001_initial
Create Date: 2026-01-29 23:30:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

revision = "0002_import_mappings"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_mappings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", mssql.NVARCHAR(length=120), nullable=False),
        sa.Column("version", mssql.NVARCHAR(length=50), nullable=False),
        sa.Column("mapping_json", mssql.NVARCHAR(length=None), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "created_at",
            mssql.DATETIME2(),
            server_default=sa.text("GETDATE()"),
            nullable=False,
        ),
        sa.UniqueConstraint("name", "version", name="uq_import_mappings_name_version"),
    )

    op.create_index(
        "ix_import_mappings_name_is_active",
        "import_mappings",
        ["name", "is_active"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_import_mappings_name_is_active", table_name="import_mappings")
    op.drop_table("import_mappings")
