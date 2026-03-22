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
    
    # Check users table
    columns = [col['name'] for col in inspector.get_columns('users')]

    # Check for missing core columns (rare but possible if created weirdly)
    if 'user_id' not in columns:
        # If user_id is missing, the table data is likely unusable or partial.
        # We truncate the table to avoid NotNullViolation when adding the column.
        op.execute('TRUNCATE users CASCADE')
        op.add_column('users', sa.Column('user_id', sa.String(), nullable=False, unique=True))
    if 'consumer_id' not in columns:
        op.add_column('users', sa.Column('consumer_id', sa.String(), nullable=False, unique=True))
    
    # Missing columns discovered in subsequent runs
    if 'name' not in columns:
        op.add_column('users', sa.Column('name', sa.String(), nullable=False))
    if 'meter_id' not in columns:
        op.add_column('users', sa.Column('meter_id', sa.String(), nullable=False))
    if 'phone' not in columns:
        op.add_column('users', sa.Column('phone', sa.String(), nullable=False))
    if 'state' not in columns:
        op.add_column('users', sa.Column('state', sa.String(), nullable=False))
    if 'discom' not in columns:
        op.add_column('users', sa.Column('discom', sa.String(), nullable=False))
        
    # Clean up incorrect columns from previous bad migrations
    if 'phone_number' in columns:
        op.drop_column('users', 'phone_number')
    if 'consumer_number' in columns:
        op.drop_column('users', 'consumer_number')
    if 'location' in columns:
        op.drop_column('users', 'location')

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
        
    # Also check notification table
    try:
        if inspector.has_table('notifications'):
            notif_columns = [col['name'] for col in inspector.get_columns('notifications')]
            
            if 'reference_id' not in notif_columns:
                op.add_column('notifications', sa.Column('reference_id', sa.String(), nullable=True))
            if 'priority' not in notif_columns:
                op.add_column('notifications', sa.Column('priority', sa.String(), server_default='medium', nullable=False))
            if 'is_read' not in notif_columns:
                op.add_column('notifications', sa.Column('is_read', sa.Boolean(), server_default='false'))
    except Exception as e:
        print(f"Error updating notifications table: {e}")
        pass


def downgrade() -> None:
    # Downgrade logic (optional, for rollback)
    op.drop_column('users', 'bill_amount')
    op.drop_column('users', 'remaining_balance')
    op.drop_column('users', 'balance_used')
    op.drop_column('users', 'active_complaint')
    op.drop_column('users', 'complaint_id')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_payment_date')
    op.drop_column('notifications', 'reference_id')
    op.drop_column('notifications', 'priority')
    op.drop_column('notifications', 'is_read')
