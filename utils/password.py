"""
Password hashing and generation utilities.
"""

from passlib.context import CryptContext
import secrets
import string

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password (str): Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password (str): Plain text password to verify
        hashed_password (str): Hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_secure_password(length: int = 12) -> str:
    """
    Generate a secure random password.

    Args:
        length (int): Length of password (default: 12)

    Returns:
        str: Generated secure password

    Example:
        password = generate_secure_password()
        # Output: "K9x#Qp2@L5vM"
    """
    # Ensure password has uppercase, lowercase, digit, and special character
    uppercase = secrets.choice(string.ascii_uppercase)
    lowercase = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice(string.punctuation)

    # Fill the rest with random characters from all categories
    remaining = length - 4
    all_chars = string.ascii_letters + string.digits + string.punctuation
    remaining_chars = ''.join(secrets.choice(all_chars) for _ in range(remaining))

    # Combine and shuffle
    password_list = list(uppercase + lowercase + digit + special + remaining_chars)
    secrets.SystemRandom().shuffle(password_list)

    return ''.join(password_list)


def generate_otp() -> str:
    """
    Generate a 6-digit OTP.

    Returns:
        str: 6-digit OTP

    Example:
        otp = generate_otp()
        # Output: "123456"
    """
    return ''.join(secrets.choice(string.digits) for _ in range(6))

