"""
Pydantic schemas for SMS & Notifications module.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


# ── Enums ────────────────────────────────────────────────────────────────────

class SMSStatus(str, Enum):
    SENT = "Sent"
    FAILED = "Failed"
    PENDING = "Pending"


class BulkCategory(str, Enum):
    OVERDUE = "overdue"
    PENDING = "pending"
    SELECTED_USERS = "selected_users"


# ── SMS Log schemas ───────────────────────────────────────────────────────────

class SMSLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sms_id: str
    user_id: str
    phone_number: str
    message: str
    status: str
    sent_at: datetime


# ── Send SMS request ──────────────────────────────────────────────────────────

class SendSMSRequest(BaseModel):
    user_id: str
    phone_number: str
    message: str


class SendSMSResponse(BaseModel):
    sms_id: str
    user_id: str
    phone_number: str
    message: str
    status: str
    sent_at: datetime


# ── Bulk SMS ──────────────────────────────────────────────────────────────────

class BulkSMSRequest(BaseModel):
    category: BulkCategory
    message: str
    user_ids: Optional[List[str]] = None


class BulkSMSResponse(BaseModel):
    sent: int
    failed: int
    total: int


# ── SMS Template schemas ──────────────────────────────────────────────────────

class SMSTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_id: str
    name: str
    body: str
    category: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class SMSTemplateUpdate(BaseModel):
    body: str

