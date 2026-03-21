from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from config.database import get_db
from schemas.notification_schema import NotificationResponse, UnreadCountResponse
from services import notification_service
from uuid import UUID

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    limit: int = 20,
    only_unread: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get latest notifications
    """
    notifications = notification_service.get_notifications(db, limit, only_unread)
    return notifications

@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(db: Session = Depends(get_db)):
    """
    Get count of unread notifications
    """
    count = notification_service.count_unread_notifications(db)
    return {"count": count}

@router.patch("/{id}/read", response_model=NotificationResponse)
def mark_read(id: UUID, db: Session = Depends(get_db)):
    """
    Mark a notification as read
    """
    notification = notification_service.mark_notification_as_read(db, str(id))
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.patch("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    """
    Mark all notifications as read
    """
    notification_service.mark_all_notifications_as_read(db)
    return {"message": "All notifications marked as read"}

