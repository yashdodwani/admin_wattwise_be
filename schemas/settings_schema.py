"""Pydantic schemas for settings and admin profile APIs."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BillingSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    billing_cycle_days: int
    late_fee_amount: float
    grace_period_days: int
    auto_disconnect_enabled: bool


class BillingSettingsUpdate(BaseModel):
    billing_cycle_days: int = Field(..., gt=0)
    late_fee_amount: float = Field(..., ge=0)
    grace_period_days: int = Field(..., ge=0)
    auto_disconnect_enabled: bool


class AdminProfileResponse(BaseModel):
    admin_id: str
    name: str
    email: str
    role: str
    created_at: datetime


class AdminProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=255)
    phone_number: Optional[str] = Field(default=None, min_length=10, max_length=20)
    password: Optional[str] = Field(default=None, min_length=8)


class NotificationPreferencesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sms_alerts_enabled: bool
    email_alerts_enabled: bool
    outage_notifications: bool
    billing_notifications: bool


class NotificationPreferencesUpdate(BaseModel):
    sms_alerts_enabled: bool
    email_alerts_enabled: bool
    outage_notifications: bool
    billing_notifications: bool

