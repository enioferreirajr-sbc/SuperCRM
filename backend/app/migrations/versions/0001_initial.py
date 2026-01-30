"""Initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-29 14:30:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "proposals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("proposal_id", sa.String(length=50), nullable=False),
        sa.Column("customer_name", sa.String(length=255), nullable=True),
        sa.Column("proposal_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=100), nullable=True),
        sa.Column("closing_date", sa.Date(), nullable=True),
        sa.Column("total_value", sa.Numeric(18, 2), nullable=True),
        sa.UniqueConstraint("proposal_id", name="uq_proposals_proposal_id"),
    )

    op.create_table(
        "proposal_details",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("proposal_id", sa.Integer(), sa.ForeignKey("proposals.id"), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=True),
        sa.Column("type_name", sa.String(length=100), nullable=True),
        sa.Column("team_name", sa.String(length=100), nullable=True),
        sa.Column("value", sa.Numeric(18, 2), nullable=True),
    )

    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("import_batches")
    op.drop_table("proposal_details")
    op.drop_table("proposals")
