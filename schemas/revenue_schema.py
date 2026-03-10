"""
Pydantic schemas for Revenue & Transactions module.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────────────

class PaymentMethod(str, Enum):
    UPI = "UPI"
    NET_BANKING = "Net Banking"
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    WALLET = "Wallet"


class TransactionStatus(str, Enum):
    SUCCESS = "Success"
    PENDING = "Pending"
    FAILED = "Failed"


# ── Transaction schemas ───────────────────────────────────────────────────────

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transaction_id: str
    user_id: str
    state: Optional[str] = None
    amount: float
    payment_method: str
    status: str
    created_at: datetime


class PaginatedTransactions(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[TransactionResponse]


# ── Revenue aggregation schemas ───────────────────────────────────────────────

class RevenueSummary(BaseModel):
    total_revenue: float
    pending_revenue: float
    average_bill_amount: float
    highest_payment: float


class RevenueByState(BaseModel):
    state: str
    revenue: float


class MonthlyRevenue(BaseModel):
    month: str
    revenue: float


class PaymentMethodDistribution(BaseModel):
    payment_method: str
    count: int
    total_amount: float


class RechargeDistribution(BaseModel):
    range_label: str
    count: int

