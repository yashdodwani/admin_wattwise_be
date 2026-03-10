"""
Password hashing and generation utilities.
"""

import bcrypt
import secrets
import string


def _to_72_bytes(password: str) -> bytes:
    """Encode a password to UTF-8 bytes and truncate to 72 bytes."""
    encoded = password.encode("utf-8")
    return encoded[:72]


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt, ensuring it is truncated to 72 bytes.

    Args:
        password (str): The plaintext password to hash.

    Returns:
        str: The hashed password.
    """
    return bcrypt.hashpw(_to_72_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a hashed password.

    Args:
        plain_password (str): The plaintext password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(_to_72_bytes(plain_password), hashed_password.encode("utf-8"))


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
