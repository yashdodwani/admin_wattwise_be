from sqlalchemy import Column, String, Boolean, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from config.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, unique=True, nullable=False)
    consumer_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    meter_id = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    state = Column(String, nullable=False)
    discom = Column(String, nullable=False)
    bill_amount = Column(Float, nullable=False)
    last_payment_date = Column(DateTime, nullable=True)
    remaining_balance = Column(Float, nullable=False)
    balance_used = Column(Float, nullable=False)
    active_complaint = Column(Boolean, default=False)
    complaint_id = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False)
