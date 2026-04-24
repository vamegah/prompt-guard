"""add org scoping to prompts, schemas, test suites

Revision ID: 0004_org_scoping
Revises: 0003_invoices
Create Date: 2026-03-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0004_org_scoping"
down_revision = "0003_invoices"
branch_labels = None
depends_on = None

DEFAULT_ORG_ID = "00000000-0000-0000-0000-000000000000"


def upgrade() -> None:
    op.execute(
        sa.text(
            "INSERT INTO organizations (id, name, created_at) "
            "VALUES (:id, 'Default', now()) "
            "ON CONFLICT (id) DO NOTHING"
        ).bindparams(id=DEFAULT_ORG_ID)
    )

    op.add_column(
        "prompts",
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=DEFAULT_ORG_ID,
        ),
    )
    op.create_foreign_key(
        "fk_prompts_org_id", "prompts", "organizations", ["org_id"], ["id"]
    )
    op.create_index("ix_prompts_org_id", "prompts", ["org_id"])
    op.alter_column("prompts", "org_id", server_default=None)

    op.add_column(
        "schemas",
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=DEFAULT_ORG_ID,
        ),
    )
    op.create_foreign_key(
        "fk_schemas_org_id", "schemas", "organizations", ["org_id"], ["id"]
    )
    op.create_index("ix_schemas_org_id", "schemas", ["org_id"])
    op.alter_column("schemas", "org_id", server_default=None)

    op.add_column(
        "test_suites",
        sa.Column(
            "org_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=DEFAULT_ORG_ID,
        ),
    )
    op.create_foreign_key(
        "fk_test_suites_org_id",
        "test_suites",
        "organizations",
        ["org_id"],
        ["id"],
    )
    op.create_index("ix_test_suites_org_id", "test_suites", ["org_id"])
    op.alter_column("test_suites", "org_id", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_test_suites_org_id", table_name="test_suites")
    op.drop_constraint("fk_test_suites_org_id", "test_suites", type_="foreignkey")
    op.drop_column("test_suites", "org_id")

    op.drop_index("ix_schemas_org_id", table_name="schemas")
    op.drop_constraint("fk_schemas_org_id", "schemas", type_="foreignkey")
    op.drop_column("schemas", "org_id")

    op.drop_index("ix_prompts_org_id", table_name="prompts")
    op.drop_constraint("fk_prompts_org_id", "prompts", type_="foreignkey")
    op.drop_column("prompts", "org_id")
