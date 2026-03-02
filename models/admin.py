"""
Database models for the WattWise Admin Portal.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Admin(Base):
    """Admin user model for authentication and authorization."""

    __tablename__ = "admins"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Admin identification
    admin_id = Column(String(10), unique=True, index=True, nullable=False)  # Format: ADM + 6 digits

    # Personal information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone_number = Column(String(15), nullable=False)

    # Organization
    descom_name = Column(String(255), nullable=False)

    # Security
    hashed_password = Column(String(255), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # OTP management
    otp_code = Column(String(6), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Admin(admin_id={self.admin_id}, name={self.name}, email={self.email})>"

