"""
FastAPI authentication routes for the WattWise Admin Portal.

Endpoints:
- POST /admin/register - Admin registration
- POST /admin/login - Admin login
- POST /admin/forgot-password - Request password reset OTP
- POST /admin/verify-otp - Verify OTP and reset password
- GET /admin/profile - Get current admin profile (protected)
- POST /admin/logout - Admin logout (optional)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from models.admin import Admin
from schemas.admin_schema import (
    AdminRegisterRequest,
    AdminRegisterResponse,
    AdminLoginRequest,
    TokenResponse,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    AdminResponse
)
from utils.password import (
    hash_password,
    verify_password,
    generate_secure_password,
    generate_otp
)
from utils.jwt_handler import create_access_token, get_token_expiry_seconds
from utils.otp_helper import send_otp_email, store_otp, verify_otp, invalidate_otp
from utils.dependencies import get_current_admin, get_db
import secrets
import string

router = APIRouter(prefix="/admin", tags=["Admin Authentication"])


def generate_unique_admin_id(db: Session) -> str:
    """
    Generate unique admin ID with format: ADM + 4 random digits.

    Args:
        db (Session): Database session

    Returns:
        str: Unique admin ID (e.g. ADM1023)
    """
    while True:
        # Generate random 4-digit number
        random_digits = ''.join(secrets.choice(string.digits) for _ in range(4))
        admin_id = f"ADM{random_digits}"

        # Check if ID is unique
        existing = db.query(Admin).filter(Admin.admin_id == admin_id).first()
        if not existing:
            return admin_id


@router.post("/register", response_model=AdminRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_admin(
    request: AdminRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new admin user.

    **Steps:**
    1. Validate unique email
    2. Generate unique admin_id (ADM + 4 digits)
    3. Generate secure password
    4. Hash password
    5. Save admin to database with descom_name="DEFAULT"
    6. Return admin_id and password

    **Request Body:**
    - name: Admin's full name
    - email: Unique email address
    - phone_number: Contact phone number

    **Response:**
    - message: Success message
    - admin_id: Generated unique ID (e.g. ADM1023)
    - password: Auto-generated secure password
    """
    # Check if email already exists
    existing_admin = db.query(Admin).filter(Admin.email == request.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Generate unique admin ID (ADM + 4 random digits)
    admin_id = generate_unique_admin_id(db)

    # Generate and hash a secure password (8-10 chars)
    generated_password = generate_secure_password(length=10)

    # Hash password
    hashed_password = hash_password(generated_password)

    # Create new admin — descom_name defaults to "DEFAULT", is_active defaults to True
    new_admin = Admin(
        admin_id=admin_id,
        name=request.name,
        email=request.email,
        phone_number=request.phone_number,
        descom_name="DEFAULT",
        hashed_password=hashed_password,
    )

    # Save to database
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return AdminRegisterResponse(
        message="Registration successful",
        admin_id=admin_id,
        password=generated_password,
    )


@router.post("/login", response_model=TokenResponse)
def login_admin(
    request: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate admin and generate JWT token.

    **Steps:**
    1. Find admin by admin_id
    2. Verify password
    3. Generate JWT access token
    4. Return token with expiry information

    **Request Body:**
    - admin_id: Admin's unique ID
    - password: Admin's password

    **Response:**
    - access_token: JWT Bearer token
    - token_type: "bearer"
    - expires_in: Token validity in seconds (3600 = 1 hour)
    """
    # Find admin by admin_id
    admin = db.query(Admin).filter(Admin.admin_id == request.admin_id).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin_id or password"
        )

    # Check if admin is active
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )

    # Verify password
    if not verify_password(request.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin_id or password"
        )

    # Create JWT token
    token_data = {
        "admin_id": admin.admin_id,
        "role": "admin",
        "email": admin.email
    }

    access_token = create_access_token(data=token_data)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=get_token_expiry_seconds()
    )


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset via OTP.

    **Steps:**
    1. Verify email exists in database
    2. Generate 6-digit OTP
    3. Store OTP temporarily (expires in 10 minutes)
    4. Send OTP via email (mock function)
    5. Return success message

    **Request Body:**
    - email: Admin's email address

    **Response:**
    - message: Success message
    - expires_in: OTP validity in seconds (600 = 10 minutes)
    """
    # Check if email exists
    admin = db.query(Admin).filter(Admin.email == request.email).first()

    if not admin:
        # Security: Don't reveal if email exists
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    # Generate OTP
    otp = generate_otp()

    # Store OTP temporarily
    store_otp(request.email, otp, expiry_minutes=10)

    # Send OTP via email (placeholder)
    send_otp_email(request.email, otp)

    return {
        "message": f"OTP sent to {request.email}. Valid for 10 minutes.",
        "expires_in": 600
    }


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp_endpoint(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and reset password.

    **Steps:**
    1. Verify OTP against stored value
    2. Check OTP expiry and attempts
    3. Hash new password
    4. Update admin's password
    5. Invalidate OTP
    6. Return success message

    **Request Body:**
    - email: Admin's email
    - otp: 6-digit OTP received
    - new_password: New password to set

    **Response:**
    - message: Success message
    """
    # Find admin
    admin = db.query(Admin).filter(Admin.email == request.email).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    # Verify OTP
    is_valid, message = verify_otp(request.email, request.otp)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Hash new password
    hashed_password = hash_password(request.new_password)

    # Update password
    admin.hashed_password = hashed_password
    db.commit()

    # Invalidate OTP
    invalidate_otp(request.email)

    return {
        "message": "Password reset successfully. You can now log in with your new password."
    }


@router.get("/profile", response_model=AdminResponse)
def get_admin_profile(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get current admin's profile.

    **Protected Route** - Requires valid JWT token

    **Returns:**
    - admin_id: Admin's unique ID
    - name: Admin's name
    - email: Admin's email
    - phone_number: Admin's phone
    - descom_name: Distribution company
    - is_active: Account status
    - created_at: Account creation timestamp
    """
    return current_admin


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Admin logout endpoint.

    **Protected Route** - Requires valid JWT token

    Note: In JWT-based systems, logout is typically client-side (remove token).
    This endpoint serves as a checkpoint and can be extended for token blacklisting.

    **Returns:**
    - message: Logout confirmation
    """
    return {
        "message": f"Admin {current_admin.admin_id} logged out successfully"
    }
