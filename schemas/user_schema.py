from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    user_id: str
    consumer_id: str
    name: str
    meter_id: str
    phone: str
    state: str
    discom: str
    bill_amount: float
    remaining_balance: float
    balance_used: float
    active_complaint: bool
    complaint_id: Optional[str]
    is_active: bool

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    state: Optional[str] = None
    discom: Optional[str] = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
