"""
Pydantic schemas for admin authentication and validation.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class AdminRegisterRequest(BaseModel):
    """Schema for admin registration request."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone_number": "1234567890"
        }
    })

    name: str = Field(..., min_length=2, max_length=255, description="Admin full name")
    email: EmailStr = Field(..., description="Unique email address")
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number")


class AdminRegisterResponse(BaseModel):
    """Schema for admin registration response."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "message": "Registration successful",
            "admin_id": "ADM1023",
            "password": "Secure@Pass1"
        }
    })

    message: str = Field(..., description="Success message")
    admin_id: str = Field(..., description="Generated unique admin ID")
    password: str = Field(..., description="Auto-generated secure password")


class AdminLoginRequest(BaseModel):
    """Schema for admin login request."""
    model_config = ConfigDict(json_schema_extra={
        "example": {"admin_id": "ADM123456", "password": "Secure@Pass123"}
    })

    admin_id: str = Field(..., description="Admin ID")
    password: str = Field(..., min_length=8, description="Password")


class TokenResponse(BaseModel):
    """Schema for token response."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "expires_in": 3600
        }
    })

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiry in seconds")


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""
    model_config = ConfigDict(json_schema_extra={"example": {"email": "john@example.com"}})

    email: EmailStr = Field(..., description="Admin email")


class VerifyOTPRequest(BaseModel):
    """Schema for OTP verification request."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "john@example.com",
            "otp": "123456",
            "new_password": "NewSecure@Pass123"
        }
    })

    email: EmailStr = Field(..., description="Admin email")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")
    new_password: str = Field(..., min_length=8, description="New password")


class TokenPayload(BaseModel):
    """Schema for JWT token payload."""

    admin_id: str = Field(..., description="Admin ID")
    role: str = Field(default="admin", description="Role (admin only)")
    email: str = Field(..., description="Admin email")
    exp: int = Field(..., description="Token expiry timestamp")


class AdminResponse(BaseModel):
    """Schema for admin profile response."""
    model_config = ConfigDict(from_attributes=True)

    admin_id: str
    name: str
    email: str
    phone_number: str
    descom_name: str
    is_active: bool
    created_at: datetime
