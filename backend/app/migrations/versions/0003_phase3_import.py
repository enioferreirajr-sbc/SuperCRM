"""Phase 3 import tables and columns

Revision ID: 0003_phase3_import
Revises: 0002_import_mappings
Create Date: 2026-01-30 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_phase3_import"
down_revision = "0002_import_mappings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("proposals", sa.Column("main_contract_id", sa.Integer(), nullable=True))
    op.add_column("proposals", sa.Column("customer_reference", sa.String(length=255), nullable=True))
    op.add_column("proposals", sa.Column("business_proposal_date", sa.Date(), nullable=True))
    op.add_column("proposals", sa.Column("last_status_date", sa.Date(), nullable=True))
    op.add_column("proposals", sa.Column("funnel_percentage", sa.String(length=100), nullable=True))
    op.add_column("proposals", sa.Column("last_note", sa.String(length=4000), nullable=True))

    op.add_column("proposal_details", sa.Column("license_of_use", sa.Numeric(18, 2), nullable=True))
    op.add_column("proposal_details", sa.Column("training", sa.Numeric(18, 2), nullable=True))
    op.add_column("proposal_details", sa.Column("monthly_fee", sa.Numeric(18, 2), nullable=True))
    op.add_column("proposal_details", sa.Column("professional_services", sa.Numeric(18, 2), nullable=True))
    op.add_column("proposal_details", sa.Column("monthly_fee_annualized", sa.Numeric(18, 2), nullable=True))
    op.add_column("proposal_details", sa.Column("total_sales", sa.Numeric(18, 2), nullable=True))

    op.add_column("import_batches", sa.Column("started_at", sa.DateTime(), nullable=True))
    op.add_column("import_batches", sa.Column("finished_at", sa.DateTime(), nullable=True))
    op.add_column("import_batches", sa.Column("total_rows", sa.Integer(), nullable=True))
    op.add_column("import_batches", sa.Column("success_rows", sa.Integer(), nullable=True))
    op.add_column("import_batches", sa.Column("error_rows", sa.Integer(), nullable=True))
    op.add_column("import_batches", sa.Column("error_message", sa.Text(), nullable=True))

    op.create_table(
        "customer",
        sa.Column("main_contract_id", sa.Integer(), primary_key=True),
        sa.Column("customer_reference", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "customer_recipient",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "main_contract_id",
            sa.Integer(),
            sa.ForeignKey("customer.main_contract_id"),
            nullable=False,
        ),
        sa.Column("recipient_name", sa.String(length=255), nullable=False),
        sa.Column("recipient_email", sa.String(length=255), nullable=False),
        sa.Column("cellphone", sa.String(length=50), nullable=True),
        sa.UniqueConstraint("main_contract_id", "recipient_email", name="uq_customer_recipient_email"),
    )

    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("product_name", sa.String(length=150), nullable=False),
        sa.UniqueConstraint("product_name", name="uq_product_name"),
    )

    op.create_table(
        "proposal_type",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("proposal_type_name", sa.String(length=150), nullable=False),
        sa.UniqueConstraint("proposal_type_name", name="uq_proposal_type_name"),
    )

    op.create_table(
        "team",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("team_name", sa.String(length=150), nullable=False),
        sa.UniqueConstraint("team_name", name="uq_team_name"),
    )

    op.create_table(
        "owner",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("owner_name", sa.String(length=150), nullable=False),
        sa.UniqueConstraint("owner_name", name="uq_owner_name"),
    )


def downgrade() -> None:
    op.drop_table("owner")
    op.drop_table("team")
    op.drop_table("proposal_type")
    op.drop_table("product")
    op.drop_table("customer_recipient")
    op.drop_table("customer")

    op.drop_column("import_batches", "error_message")
    op.drop_column("import_batches", "error_rows")
    op.drop_column("import_batches", "success_rows")
    op.drop_column("import_batches", "total_rows")
    op.drop_column("import_batches", "finished_at")
    op.drop_column("import_batches", "started_at")

    op.drop_column("proposal_details", "total_sales")
    op.drop_column("proposal_details", "monthly_fee_annualized")
    op.drop_column("proposal_details", "professional_services")
    op.drop_column("proposal_details", "monthly_fee")
    op.drop_column("proposal_details", "training")
    op.drop_column("proposal_details", "license_of_use")

    op.drop_column("proposals", "last_note")
    op.drop_column("proposals", "funnel_percentage")
    op.drop_column("proposals", "last_status_date")
    op.drop_column("proposals", "business_proposal_date")
    op.drop_column("proposals", "customer_reference")
    op.drop_column("proposals", "main_contract_id")
