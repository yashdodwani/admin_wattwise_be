"""
SMS & Notifications API Router.

Provides endpoints for:
- Listing SMS logs
- Sending a single SMS
- Sending bulk SMS (overdue / pending / selected users)
- Retrying a failed SMS
- Listing SMS templates
- Updating SMS template body
"""

import uuid
import datetime
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import cast, String

from config.database import get_db
from models.sms import SMSLog, SMSTemplate
from models.user import User
from services.notification_service import create_system_notification
from schemas.sms_schema import (
    SMSLogResponse,
    SendSMSRequest,
    SendSMSResponse,
    BulkSMSRequest,
    BulkSMSResponse,
    SMSTemplateResponse,
    SMSTemplateUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sms", tags=["SMS & Notifications"])


# ─────────────────────────────────────────────────────────────────────────────
# Internal helper – simulated SMS gateway
# ─────────────────────────────────────────────────────────────────────────────

def send_sms(phone: str, message: str) -> bool:
    """
    Placeholder SMS sender.

    Replace the body of this function with a real SMS gateway call
    (e.g. Twilio, MSG91, etc.).

    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    logger.info(f"[SMS GATEWAY] Sending to {phone}: {message[:60]}…")
    # Simulate success for all numbers
    return True


def _generate_sms_id() -> str:
    """Generate a human-readable SMS log identifier."""
    return f"SMS-{uuid.uuid4().hex[:8].upper()}"


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/sms/logs
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/logs", response_model=List[SMSLogResponse])
def get_sms_logs(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    """
    Return a paginated list of all SMS log entries.

    Each entry contains: sms_id, user_id, phone_number, message,
    status, and sent_at timestamp.
    """
    offset = (page - 1) * page_size
    logs = (
        db.query(SMSLog)
        .order_by(SMSLog.sent_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return logs


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/sms/send
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/send", response_model=SendSMSResponse, status_code=201)
def send_single_sms(payload: SendSMSRequest, db: Session = Depends(get_db)):
    """
    Send an SMS to a single user.

    - Calls the `send_sms()` gateway function.
    - Persists the attempt (with final status) in the SMSLogs table.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    success = send_sms(payload.phone_number, payload.message)
    status = "Sent" if success else "Failed"

    log = SMSLog(
        sms_id=_generate_sms_id(),
        user_id=payload.user_id,
        phone_number=payload.phone_number,
        message=payload.message,
        status=status,
        sent_at=now,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # Create notification for SMS status
    create_system_notification(
        db=db,
        title=f"SMS {status}",
        message=f"SMS to {payload.phone_number} {status.lower()}",
        type="sms",
        priority="high" if status == "Failed" else "low",
        reference_id=str(log.id)
    )

    return SendSMSResponse(
        sms_id=log.sms_id,
        user_id=log.user_id,
        phone_number=log.phone_number,
        message=log.message,
        status=log.status,
        sent_at=log.sent_at,
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/sms/send-bulk
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/send-bulk", response_model=BulkSMSResponse, status_code=201)
def send_bulk_sms(payload: BulkSMSRequest, db: Session = Depends(get_db)):
    """
    Send SMS to multiple users based on a category.

    Categories:
    - **overdue**        — users whose remaining_balance is 0
    - **pending**        — users with active_complaint == True
    - **selected_users** — explicit list supplied in `user_ids`

    Saves one SMSLog entry per user.
    """
    category = payload.category.value

    if category == "selected_users":
        if not payload.user_ids:
            raise HTTPException(
                status_code=400,
                detail="user_ids is required when category is 'selected_users'.",
            )
        users = db.query(User).filter(User.user_id.in_(payload.user_ids)).all()

    elif category == "overdue":
        users = db.query(User).filter(User.remaining_balance <= 0).all()

    elif category == "pending":
        users = db.query(User).filter(User.active_complaint == True).all()  # noqa: E712

    else:
        raise HTTPException(status_code=400, detail=f"Unknown category: {category}")

    sent_count = 0
    failed_count = 0
    now = datetime.datetime.now(datetime.timezone.utc)

    for user in users:
        # Pylance might complain about user.phone type, but SQLAlchemy handles it.
        success = send_sms(user.phone, payload.message) # type: ignore
        status = "Sent" if success else "Failed"

        log = SMSLog(
            sms_id=_generate_sms_id(),
            user_id=user.user_id, # type: ignore
            phone_number=user.phone, # type: ignore
            message=payload.message,
            status=status,
            sent_at=now,
        )
        db.add(log)
        if success:
            sent_count += 1
        else:
            failed_count += 1

    db.commit()

    # Notification for bulk SMS
    create_system_notification(
        db=db,
        title=f"Bulk SMS Sent ({category})",
        message=f"Sent: {sent_count}, Failed: {failed_count} to '{category}' users.",
        type="sms",
        priority="low" if failed_count == 0 else "medium"
    )

    return BulkSMSResponse(
        sent=sent_count,
        failed=failed_count,
        total=sent_count + failed_count,
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/sms/retry/{id}
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/retry/{id}", response_model=SendSMSResponse)
def retry_sms(
    id: str = Path(..., description="UUID or sms_id of the SMS log entry to retry"),
    db: Session = Depends(get_db),
):
    """
    Retry sending a previously failed SMS.

    Looks up the SMSLog by its UUID primary key or sms_id, attempts
    resending, and updates the status in-place.
    """
    # Support both UUID primary key and friendly sms_id
    log = (
        db.query(SMSLog).filter(SMSLog.sms_id == id).first()
        or db.query(SMSLog).filter(cast(SMSLog.id, String) == id).first()
    )

    if not log:
        raise HTTPException(status_code=404, detail=f"SMS log '{id}' not found.")

    if log.status == "Sent":
        raise HTTPException(status_code=400, detail="SMS was already sent successfully.")

    success = send_sms(log.phone_number, log.message) # type: ignore
    status = "Sent" if success else "Failed"

    log.status = status
    log.sent_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(log)

    # Notification for retry result
    create_system_notification(
        db=db,
        title=f"SMS Retry {status}",
        message=f"Retried SMS to {log.phone_number}: {status}", # type: ignore
        type="sms",
        priority="high" if status == "Failed" else "low",
        reference_id=str(log.id) # type: ignore
    )

    return SendSMSResponse(
        sms_id=log.sms_id, # type: ignore
        user_id=log.user_id, # type: ignore
        phone_number=log.phone_number, # type: ignore
        message=log.message, # type: ignore
        status=log.status, # type: ignore
        sent_at=log.sent_at, # type: ignore
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/sms/templates
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/templates", response_model=List[SMSTemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    """
    Return all pre-defined SMS templates stored in the database.
    """
    return db.query(SMSTemplate).order_by(SMSTemplate.name).all()


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/sms/templates/{id}
# ─────────────────────────────────────────────────────────────────────────────

@router.put("/templates/{id}", response_model=SMSTemplateResponse)
def update_template(
    id: str = Path(..., description="UUID or template_id of the SMS template"),
    payload: SMSTemplateUpdate = ...,
    db: Session = Depends(get_db),
):
    """
    Update the message body of a specific SMS template.

    Accepts both UUID primary key and human-readable template_id.
    """
    template = (
        db.query(SMSTemplate).filter(SMSTemplate.template_id == id).first()
        or db.query(SMSTemplate).filter(cast(SMSTemplate.id, String) == id).first()
    )

    if not template:
        raise HTTPException(status_code=404, detail=f"SMS template '{id}' not found.")

    template.body = payload.body
    template.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(template)

    return template

