from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str # complaint, sms, emergency, system, user_activity
    reference_id: Optional[str] = None
    priority: str = 'medium' # low, medium, high, critical

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: UUID
    title: str
    message: str
    type: str
    reference_id: Optional[str]
    is_read: bool
    priority: str
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]
    unread_count: int

class UnreadCountResponse(BaseModel):
    count: int

