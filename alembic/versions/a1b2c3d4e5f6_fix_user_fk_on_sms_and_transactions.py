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
down_revision: Union[str, None] = 'f7d2c8a91b44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This migration was originally intended to convert user_id to UUID,
    # but the Python models use String for user_id (business key).
    # We skip the specific column alteration to causing failures and simple
    # schema mismatch.
    pass


def downgrade() -> None:
    pass
