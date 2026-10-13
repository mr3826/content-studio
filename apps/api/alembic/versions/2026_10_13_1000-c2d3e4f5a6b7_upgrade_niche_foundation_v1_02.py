"""upgrade_niche_foundation_v1_02

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-10-13 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c2d3e4f5a6b7"
down_revision: Union[str, None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add versioning and enriched profile columns to niche_profiles
    with op.batch_alter_table("niche_profiles") as batch_op:
        batch_op.add_column(
            sa.Column("target_skill_levels", sa.JSON(), nullable=False, server_default="[]")
        )
        batch_op.add_column(
            sa.Column("audience_goals", sa.JSON(), nullable=False, server_default="[]")
        )
        batch_op.add_column(
            sa.Column("topic_exceptions", sa.JSON(), nullable=False, server_default="[]")
        )
        batch_op.add_column(
            sa.Column("policy_version", sa.Integer(), nullable=False, server_default="1")
        )
        batch_op.add_column(
            sa.Column("policy_fingerprint", sa.String(length=64), nullable=True)
        )

    # 2. Create niche_policy_audits table
    op.create_table(
        "niche_policy_audits",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("niche_id", sa.String(length=32), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("change_summary", sa.Text(), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_niche_policy_audits_niche_id"),
        "niche_policy_audits",
        ["niche_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_niche_policy_audits_version"),
        "niche_policy_audits",
        ["version"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_niche_policy_audits_version"), table_name="niche_policy_audits")
    op.drop_index(op.f("ix_niche_policy_audits_niche_id"), table_name="niche_policy_audits")
    op.drop_table("niche_policy_audits")

    with op.batch_alter_table("niche_profiles") as batch_op:
        batch_op.drop_column("policy_fingerprint")
        batch_op.drop_column("policy_version")
        batch_op.drop_column("topic_exceptions")
        batch_op.drop_column("audience_goals")
        batch_op.drop_column("target_skill_levels")
