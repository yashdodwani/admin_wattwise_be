from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from schemas.user_schema import UserResponse, UserUpdate
from models.user import User
from utils.dependencies import get_db

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/", response_model=List[UserResponse])
def get_users(
    state: Optional[str] = None,
    discom: Optional[str] = None,
    active: Optional[bool] = None,
    amount_gt: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(User)

    if state:
        query = query.filter(User.state == state)
    if discom:
        query = query.filter(User.discom == discom)
    if active is not None:
        query = query.filter(User.is_active == active)
    if amount_gt is not None:
        query = query.filter(User.bill_amount > amount_gt)

    return query.all()

@router.get("/{id}", response_model=UserResponse)
def get_user(id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{id}", response_model=UserResponse)
def update_user(id: UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user

@router.patch("/{id}/toggle-active", response_model=UserResponse)
def toggle_user_active(id: UUID, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user

@router.get("/{id}/balance")
def get_user_balance(id: UUID, period: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Placeholder logic for balance analytics
    return {
        "user_id": user.user_id,
        "remaining_balance": user.remaining_balance,
        "balance_used": user.balance_used,
        "period": period
    }
