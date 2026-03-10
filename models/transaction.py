"""
SQLAlchemy model for Transactions / Recharge payments.
"""

import uuid
import datetime
from sqlalchemy import Column, String, Float, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum as PyEnum
from config.database import Base


class PaymentMethod(str, PyEnum):
    UPI = "UPI"
    NET_BANKING = "Net Banking"
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    WALLET = "Wallet"


class TransactionStatus(str, PyEnum):
    SUCCESS = "Success"
    PENDING = "Pending"
    FAILED = "Failed"


class Transaction(Base):
    """Transaction model representing a payment / recharge record."""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, nullable=False)          # references users.user_id (loose FK)
    state = Column(String, nullable=True)             # denormalised for easy aggregation
    amount = Column(Float, nullable=False)
    payment_method = Column(
        SAEnum(
            "UPI", "Net Banking", "Credit Card", "Debit Card", "Wallet",
            name="paymentmethod_enum",
        ),
        nullable=False,
    )
    status = Column(
        SAEnum("Success", "Pending", "Failed", name="transactionstatus_enum"),
        nullable=False,
        default="Pending",
    )
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

