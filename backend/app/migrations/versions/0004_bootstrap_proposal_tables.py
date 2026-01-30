"""Rebuild proposal tables to match bootstrap mapping

Revision ID: 0004_bootstrap_proposal_tables
Revises: 0003_phase3_import
Create Date: 2026-01-30 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

revision = "0004_bootstrap_proposal_tables"
down_revision = "0003_phase3_import"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("proposal_details")
    op.drop_table("proposals")

    op.create_table(
        "proposal",
        sa.Column("proposal_id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("main_contract_id", sa.Integer(), nullable=False),
        sa.Column("customer_reference", mssql.NVARCHAR(length=255), nullable=True),
        sa.Column("proposal_name", mssql.NVARCHAR(length=255), nullable=True),
        sa.Column("recipient_name", mssql.NVARCHAR(length=255), nullable=True),
        sa.Column("recipient_email", mssql.NVARCHAR(length=255), nullable=True),
        sa.Column("proposal_status", mssql.NVARCHAR(length=255), nullable=True),
        sa.Column("business_proposal_date", sa.Date(), nullable=True),
        sa.Column("last_status_date", sa.Date(), nullable=True),
        sa.Column("funnel_percentage", mssql.NVARCHAR(length=100), nullable=False),
        sa.Column("last_note", mssql.NVARCHAR(length=4000), nullable=True),
    )

    op.create_table(
        "proposal_detail",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "proposal_id",
            sa.Integer(),
            sa.ForeignKey("proposal.proposal_id"),
            nullable=False,
        ),
        sa.Column("proposal_type_name", mssql.NVARCHAR(length=100), nullable=False),
        sa.Column("product_name", mssql.NVARCHAR(length=100), nullable=False),
        sa.Column("team_name", mssql.NVARCHAR(length=100), nullable=False),
        sa.Column("owner", mssql.NVARCHAR(length=100), nullable=False),
        sa.Column(
            "license_of_use",
            sa.Numeric(18, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "training",
            sa.Numeric(18, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "monthly_fee",
            sa.Numeric(18, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "professional_services",
            sa.Numeric(18, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "monthly_fee_annualized",
            sa.Numeric(18, 2),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("total_sales", sa.Numeric(18, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("proposal_detail")
    op.drop_table("proposal")
