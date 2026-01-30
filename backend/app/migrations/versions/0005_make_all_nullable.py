"""Make all non-PK columns nullable

Revision ID: 0005_make_all_nullable
Revises: 0004_bootstrap_proposal_tables
Create Date: 2026-01-30 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0005_make_all_nullable"
down_revision = "0004_bootstrap_proposal_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    schema = "dbo"

    for table_name in inspector.get_table_names(schema=schema):
        pk = inspector.get_pk_constraint(table_name, schema=schema) or {}
        pk_columns = set(pk.get("constrained_columns") or [])

        for column in inspector.get_columns(table_name, schema=schema):
            column_name = column["name"]
            if column_name in pk_columns:
                continue
            if column.get("nullable", True):
                continue
            existing_type = column["type"]
            op.alter_column(
                table_name,
                column_name,
                existing_type=existing_type,
                nullable=True,
                schema=schema,
            )


def downgrade() -> None:
    pass
