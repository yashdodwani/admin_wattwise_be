"""
OTP (One-Time Password) and email utilities.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Logger setup
logger = logging.getLogger(__name__)

# In-memory OTP storage (in production, use Redis)
otp_storage: Dict[str, Dict] = {}


def send_otp_email(email: str, otp: str) -> bool:
    """
    Send OTP via email using SMTP configuration from environment variables.
    """
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_name = os.getenv("SENDER_NAME", "WattWise Admin")

    if not all([smtp_server, smtp_username, smtp_password]):
        logger.warning("SMTP configuration missing. Printing OTP to console.")
        print(f"✉️  [TEST MODE] OTP: {otp} sent to {email}")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = f"{sender_name} <{sender_email}>"
        msg['To'] = email
        msg['Subject'] = "Your WattWise Admin OTP Code"

        body = f"""
        <html>
          <body>
            <h2>WattWise Admin Portal Login</h2>
            <p>Your One-Time Password (OTP) is:</p>
            <h1 style="color: #4CAF50; font-size: 32px;">{otp}</h1>
            <p>This code is valid for 10 minutes.</p>
            <p>If you did not request this code, please ignore this email.</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        logger.info(f"OTP email sent successfully to {email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        # Fallback to console in development
        print(f"✉️  [TEST MODE (Fallback)] OTP: {otp} sent to {email}")
        return False


def store_otp(email: str, otp: str, expiry_minutes: int = 10) -> None:
    """
    Store OTP temporarily (in-memory).

    Note: In production, use Redis with automatic expiry.

    Args:
        email (str): Email address
        otp (str): OTP code
        expiry_minutes (int): OTP validity duration
    """
    expiry_time = datetime.utcnow() + timedelta(minutes=expiry_minutes)
    otp_storage[email] = {
        "otp": otp,
        "expiry": expiry_time,
        "attempts": 0
    }
    logger.info(f"OTP stored for {email}, expires at {expiry_time}")


def verify_otp(email: str, otp: str, max_attempts: int = 3) -> tuple[bool, str]:
    """
    Verify OTP against stored value.

    Args:
        email (str): Email address
        otp (str): OTP to verify
        max_attempts (int): Maximum allowed attempts

    Returns:
        tuple[bool, str]: (is_valid, message)

    Example:
        is_valid, message = verify_otp("john@example.com", "123456")
    """
    if email not in otp_storage:
        return False, "OTP not found or expired"

    stored_otp_data = otp_storage[email]

    # Check expiry
    if datetime.utcnow() > stored_otp_data["expiry"]:
        del otp_storage[email]
        return False, "OTP has expired"

    # Check attempts
    if stored_otp_data["attempts"] >= max_attempts:
        del otp_storage[email]
        return False, "Maximum OTP attempts exceeded"

    # Verify OTP
    if stored_otp_data["otp"] != otp:
        stored_otp_data["attempts"] += 1
        return False, f"Invalid OTP ({max_attempts - stored_otp_data['attempts']} attempts remaining)"

    # OTP verified successfully
    del otp_storage[email]
    return True, "OTP verified successfully"


def invalidate_otp(email: str) -> None:
    """
    Invalidate OTP for an email address.

    Args:
        email (str): Email address
    """
    if email in otp_storage:
        del otp_storage[email]
        logger.info(f"OTP invalidated for {email}")


def get_otp_remaining_time(email: str) -> Optional[int]:
    """
    Get remaining validity time for OTP in seconds.

    Args:
        email (str): Email address

    Returns:
        Optional[int]: Remaining seconds, None if OTP not found
    """
    if email not in otp_storage:
        return None

    expiry = otp_storage[email]["expiry"]
    remaining = (expiry - datetime.utcnow()).total_seconds()

    return max(0, int(remaining))
