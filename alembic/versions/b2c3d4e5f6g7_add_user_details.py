"""add_user_details

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use inspector to check if columns exist before creating them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'bill_amount' not in columns:
        op.add_column('users', sa.Column('bill_amount', sa.Float(), server_default='0.0', nullable=False))
    if 'remaining_balance' not in columns:
        op.add_column('users', sa.Column('remaining_balance', sa.Float(), server_default='0.0', nullable=False))
    if 'balance_used' not in columns:
        op.add_column('users', sa.Column('balance_used', sa.Float(), server_default='0.0', nullable=False))
    if 'active_complaint' not in columns:
        op.add_column('users', sa.Column('active_complaint', sa.Boolean(), server_default='false', nullable=True))
    if 'complaint_id' not in columns:
        op.add_column('users', sa.Column('complaint_id', sa.String(), nullable=True))
    if 'is_active' not in columns:
        op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=True))
    if 'last_payment_date' not in columns:
        op.add_column('users', sa.Column('last_payment_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Downgrade logic (optional, for rollback)
    op.drop_column('users', 'bill_amount')
    op.drop_column('users', 'remaining_balance')
    op.drop_column('users', 'balance_used')
    op.drop_column('users', 'active_complaint')
    op.drop_column('users', 'complaint_id')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_payment_date')

