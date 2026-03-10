"""
SQLAlchemy models for SMS Logs and SMS Templates.
"""

import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from config.database import Base


class SMSLog(Base):
    """Stores every outbound SMS attempt."""

    __tablename__ = "sms_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sms_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    status = Column(
        SAEnum("Sent", "Failed", "Pending", name="smsstatus_enum"),
        nullable=False,
        default="Pending",
    )
    sent_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


class SMSTemplate(Base):
    """Pre-defined message templates used for bulk / automated SMS."""

    __tablename__ = "sms_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String, nullable=True)          # e.g. overdue, welcome, reminder
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)

