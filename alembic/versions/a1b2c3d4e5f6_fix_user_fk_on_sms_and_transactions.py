"""fix_user_fk_on_sms_and_transactions

Alter sms_logs.user_id and transactions.user_id from VARCHAR to UUID
and add proper foreign key constraints referencing users.id.

Revision ID: a1b2c3d4e5f6
Revises: 033fea8183f9
Create Date: 2026-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '033fea8183f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── sms_logs ──────────────────────────────────────────────────────────────
    # Drop the old string column and recreate as UUID with FK.
    # NOTE: existing rows must have valid UUID values (or the table must be
    # empty) for the USING cast to succeed.
    op.alter_column(
        'sms_logs',
        'user_id',
        existing_type=sa.String(),
        type_=postgresql.UUID(as_uuid=True),
        postgresql_using='user_id::uuid',
        nullable=False,
    )
    op.create_foreign_key(
        'fk_sms_logs_user_id',
        'sms_logs',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE',
    )

    # ── transactions ──────────────────────────────────────────────────────────
    op.alter_column(
        'transactions',
        'user_id',
        existing_type=sa.String(),
        type_=postgresql.UUID(as_uuid=True),
        postgresql_using='user_id::uuid',
        nullable=False,
    )
    op.create_foreign_key(
        'fk_transactions_user_id',
        'transactions',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    # ── transactions ──────────────────────────────────────────────────────────
    op.drop_constraint('fk_transactions_user_id', 'transactions', type_='foreignkey')
    op.alter_column(
        'transactions',
        'user_id',
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.String(),
        postgresql_using='user_id::text',
        nullable=False,
    )

    # ── sms_logs ──────────────────────────────────────────────────────────────
    op.drop_constraint('fk_sms_logs_user_id', 'sms_logs', type_='foreignkey')
    op.alter_column(
        'sms_logs',
        'user_id',
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.String(),
        postgresql_using='user_id::text',
        nullable=False,
    )
