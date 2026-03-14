"""SQLAlchemy models for platform settings and notification preferences."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer

from config.database import Base


class BillingSettings(Base):
    """Global billing settings used by admin configuration APIs."""

    __tablename__ = "billing_settings"

    id = Column(Integer, primary_key=True, index=True)
    billing_cycle_days = Column(Integer, nullable=False, default=30)
    late_fee_amount = Column(Float, nullable=False, default=0.0)
    grace_period_days = Column(Integer, nullable=False, default=5)
    auto_disconnect_enabled = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationPreference(Base):
    """Per-admin notification preferences for alerts and reminders."""

    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False, unique=True, index=True)
    sms_alerts_enabled = Column(Boolean, nullable=False, default=True)
    email_alerts_enabled = Column(Boolean, nullable=False, default=True)
    outage_notifications = Column(Boolean, nullable=False, default=True)
    billing_notifications = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

