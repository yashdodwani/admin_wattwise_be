from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from config.database import Base

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # complaint, sms, emergency, system, user_activity
    reference_id = Column(String, nullable=True) # complaint_id, sms_id, user_id
    is_read = Column(Boolean, default=False, index=True)
    priority = Column(String, nullable=False, default='medium') # low, medium, high, critical
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

