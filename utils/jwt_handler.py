"""
JWT token creation and validation utilities.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data (Dict): Data to encode in token (admin_id, role, email)
        expires_delta (Optional[timedelta]): Token expiry duration

    Returns:
        str: Encoded JWT token

    Example:
        token = create_access_token({
            "admin_id": "ADM123456",
            "role": "admin",
            "email": "john@example.com"
        })
    """
    to_encode = data.copy()

    # Set expiry time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Encode JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode a JWT token.

    Args:
        token (str): JWT token to verify

    Returns:
        Optional[Dict]: Decoded token data if valid, None if invalid

    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        return None


def get_token_expiry_seconds() -> int:
    """
    Get token expiry duration in seconds.

    Returns:
        int: Token expiry in seconds
    """
    return ACCESS_TOKEN_EXPIRE_MINUTES * 60

