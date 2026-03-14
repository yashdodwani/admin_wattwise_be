"""Settings and admin profile API routes."""

from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from models.admin import Admin
from models.settings import BillingSettings, NotificationPreference
from schemas.settings_schema import (
    AdminProfileResponse,
    AdminProfileUpdate,
    BillingSettingsResponse,
    BillingSettingsUpdate,
    NotificationPreferencesResponse,
    NotificationPreferencesUpdate,
)
from utils.dependencies import get_current_admin, get_db
from utils.password import hash_password

settings_router = APIRouter(prefix="/api", tags=["Settings"])
router = settings_router


def _get_or_create_billing_settings(db: Session) -> BillingSettings:
    settings_row = cast(BillingSettings | None, db.query(BillingSettings).order_by(BillingSettings.id.asc()).first())
    if settings_row:
        return settings_row

    settings_row = BillingSettings()
    db.add(settings_row)
    db.commit()
    db.refresh(settings_row)
    return cast(BillingSettings, settings_row)


def _get_or_create_notification_preferences(db: Session, admin_pk: int) -> NotificationPreference:
    prefs_row = cast(
        NotificationPreference | None,
        db.query(NotificationPreference).filter(NotificationPreference.admin_id == admin_pk).first(),
    )
    if prefs_row:
        return prefs_row

    prefs_row = NotificationPreference(admin_id=admin_pk)
    db.add(prefs_row)
    db.commit()
    db.refresh(prefs_row)
    return cast(NotificationPreference, prefs_row)


@settings_router.get("/settings/billing", response_model=BillingSettingsResponse)
def get_billing_settings(db: Session = Depends(get_db)):
    """Return global billing configuration settings."""
    return _get_or_create_billing_settings(db)


@settings_router.put("/settings/billing", response_model=BillingSettingsResponse)
def update_billing_settings(payload: BillingSettingsUpdate, db: Session = Depends(get_db)):
    """Update global billing configuration settings."""
    settings = _get_or_create_billing_settings(db)
    settings.billing_cycle_days = payload.billing_cycle_days
    settings.late_fee_amount = payload.late_fee_amount
    settings.grace_period_days = payload.grace_period_days
    settings.auto_disconnect_enabled = payload.auto_disconnect_enabled

    db.commit()
    db.refresh(settings)
    return settings


@settings_router.get("/admin/profile", response_model=AdminProfileResponse)
def get_admin_profile(current_admin: Admin = Depends(get_current_admin)):
    """Return the authenticated admin profile."""
    return AdminProfileResponse(
        admin_id=current_admin.admin_id,
        name=current_admin.name,
        email=current_admin.email,
        role="admin",
        created_at=current_admin.created_at,
    )


@settings_router.put("/admin/profile", response_model=AdminProfileResponse)
def update_admin_profile(
    payload: AdminProfileUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update editable admin profile fields and hash password when provided."""
    updates = payload.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No profile fields provided for update.",
        )

    if payload.name is not None:
        current_admin.name = payload.name
    if payload.phone_number is not None:
        current_admin.phone_number = payload.phone_number
    if payload.password is not None:
        current_admin.hashed_password = hash_password(payload.password)

    db.commit()
    db.refresh(current_admin)

    return AdminProfileResponse(
        admin_id=current_admin.admin_id,
        name=current_admin.name,
        email=current_admin.email,
        role="admin",
        created_at=current_admin.created_at,
    )


@settings_router.get("/settings/notifications", response_model=NotificationPreferencesResponse)
def get_notification_preferences(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Return notification preferences for the authenticated admin."""
    return _get_or_create_notification_preferences(db, current_admin.id)


@settings_router.put("/settings/notifications", response_model=NotificationPreferencesResponse)
def update_notification_preferences(
    payload: NotificationPreferencesUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update notification preferences for the authenticated admin."""
    prefs = _get_or_create_notification_preferences(db, current_admin.id)
    prefs.sms_alerts_enabled = payload.sms_alerts_enabled
    prefs.email_alerts_enabled = payload.email_alerts_enabled
    prefs.outage_notifications = payload.outage_notifications
    prefs.billing_notifications = payload.billing_notifications

    db.commit()
    db.refresh(prefs)
    return prefs

