"""
FastAPI dependencies for authentication and authorization.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from config.database import get_db
try:
    # Try relative import first (when imported as a module)
    from ..utils.jwt_handler import verify_token
    from ..models.admin import Admin
    from ..schemas.admin_schema import TokenPayload
except ImportError:
    # Fallback to absolute import (when run directly)
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.jwt_handler import verify_token
    from models.admin import Admin
    from schemas.admin_schema import TokenPayload

security = HTTPBearer()



def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Admin:
    """
    Dependency to get current authenticated admin from JWT token.

    Args:
        credentials (HTTPAuthorizationCredentials): Bearer token from header
        db (Session): Database session

    Returns:
        Admin: Current admin user

    Raises:
        HTTPException: If token is invalid or admin not found
    """
    token = credentials.credentials

    # Verify token
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract admin_id from token
    admin_id: str = payload.get("admin_id")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch admin from database
    admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if admin is active
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    return admin


def verify_admin_role(
    current_admin: Admin = Depends(get_current_admin)
) -> Admin:
    """
    Verify that the current user has admin role.

    Args:
        current_admin (Admin): Current authenticated admin

    Returns:
        Admin: Current admin if valid

    Raises:
        HTTPException: If user is not an admin
    """
    # In this system, all authenticated users are admins
    # This dependency is for future extensibility (e.g., super-admin roles)
    return current_admin
