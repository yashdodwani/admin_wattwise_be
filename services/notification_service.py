from sqlalchemy.orm import Session
from models.notification import Notification
from schemas.notification_schema import NotificationCreate

def create_notification(db: Session, notification_data: NotificationCreate):
    """
    Service function to create a new notification
    """
    new_notification = Notification(
        title=notification_data.title,
        message=notification_data.message,
        type=notification_data.type,
        reference_id=notification_data.reference_id,
        is_read=False,
        priority=notification_data.priority
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

def create_system_notification(
    db: Session,
    title: str,
    message: str,
    type: str,
    priority: str = "medium",
    reference_id: str = None
):
    """
    Helper to easily create notifications from other modules without importing the schema.
    """
    from schemas.notification_schema import NotificationCreate

    notification_data = NotificationCreate(
        title=title,
        message=message,
        type=type,
        priority=priority,
        reference_id=reference_id
    )
    return create_notification(db, notification_data)

def get_notifications(db: Session, limit: int = 20, only_unread: bool = False):
    """
    Get notifications with filters
    """
    query = db.query(Notification)

    if only_unread:
        query = query.filter(Notification.is_read == False)

    return query.order_by(Notification.created_at.desc()).limit(limit).all()

def count_unread_notifications(db: Session) -> int:
    """
    Count unread notifications
    """
    return db.query(Notification).filter(Notification.is_read == False).count()

def mark_notification_as_read(db: Session, notification_id: str):
    """
    Mark a notification as read
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if notification:
        notification.is_read = True
        db.commit()
        db.refresh(notification)
    return notification

def mark_all_notifications_as_read(db: Session):
    """
    Mark all notifications as read
    """
    # This might be slow if there are many unread notifications,
    # but for an admin dashboard it should be fine.
    # A bulk update is more efficient.
    db.query(Notification).filter(Notification.is_read == False).update({Notification.is_read: True})
    db.commit()
