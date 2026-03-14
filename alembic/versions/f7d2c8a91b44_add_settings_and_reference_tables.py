"""add_settings_and_reference_tables

Revision ID: f7d2c8a91b44
Revises: 8ac1a94203cd
Create Date: 2026-03-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f7d2c8a91b44"
down_revision: Union[str, None] = "8ac1a94203cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "billing_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("billing_cycle_days", sa.Integer(), nullable=False),
        sa.Column("late_fee_amount", sa.Float(), nullable=False),
        sa.Column("grace_period_days", sa.Integer(), nullable=False),
        sa.Column("auto_disconnect_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_billing_settings_id"), "billing_settings", ["id"], unique=False)

    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("sms_alerts_enabled", sa.Boolean(), nullable=False),
        sa.Column("email_alerts_enabled", sa.Boolean(), nullable=False),
        sa.Column("outage_notifications", sa.Boolean(), nullable=False),
        sa.Column("billing_notifications", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["admin_id"], ["admins.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notification_preferences_admin_id"), "notification_preferences", ["admin_id"], unique=True)
    op.create_index(op.f("ix_notification_preferences_id"), "notification_preferences", ["id"], unique=False)

    op.create_table(
        "states",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_states_id"), "states", ["id"], unique=False)
    op.create_index(op.f("ix_states_name"), "states", ["name"], unique=True)

    op.create_table(
        "discoms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("state_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["state_id"], ["states.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "state_id", name="uq_discom_name_state"),
    )
    op.create_index(op.f("ix_discoms_id"), "discoms", ["id"], unique=False)
    op.create_index(op.f("ix_discoms_name"), "discoms", ["name"], unique=False)
    op.create_index(op.f("ix_discoms_state_id"), "discoms", ["state_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_discoms_state_id"), table_name="discoms")
    op.drop_index(op.f("ix_discoms_name"), table_name="discoms")
    op.drop_index(op.f("ix_discoms_id"), table_name="discoms")
    op.drop_table("discoms")

    op.drop_index(op.f("ix_states_name"), table_name="states")
    op.drop_index(op.f("ix_states_id"), table_name="states")
    op.drop_table("states")

    op.drop_index(op.f("ix_notification_preferences_id"), table_name="notification_preferences")
    op.drop_index(op.f("ix_notification_preferences_admin_id"), table_name="notification_preferences")
    op.drop_table("notification_preferences")

    op.drop_index(op.f("ix_billing_settings_id"), table_name="billing_settings")
    op.drop_table("billing_settings")

