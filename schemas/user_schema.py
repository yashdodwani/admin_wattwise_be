from pydantic import BaseModel
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
    name: Optional[str]
    phone: Optional[str]
    state: Optional[str]
    discom: Optional[str]

class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        orm_mode = True
