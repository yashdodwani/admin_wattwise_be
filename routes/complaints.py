from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from schemas.complaint_schema import ComplaintResponse, ComplaintUpdate, ComplaintCreate
from models.complaint import Complaint
from utils.dependencies import get_db
from services.notification_service import create_system_notification
import datetime

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

@router.post("/", response_model=ComplaintResponse, status_code=201)
def create_complaint(complaint: ComplaintCreate, db: Session = Depends(get_db)):
    """
    Create a new complaint and trigger a notification.
    """
    db_complaint = Complaint(
        **complaint.model_dump(),
        created_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)

    # Create notification for new complaint
    create_system_notification(
        db=db,
        title="New Complaint Raised",
        message=f"New complaint {db_complaint.complaint_id} ({db_complaint.issue_type}) created.",
        type="complaint",
        priority="high" if complaint.priority == "High" else "medium",
        reference_id=str(db_complaint.id)
    )

    return db_complaint

@router.get("/", response_model=List[ComplaintResponse])
def get_complaints(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)

    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)

    return query.all()

@router.get("/{id}", response_model=ComplaintResponse)
def get_complaint(id: UUID, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@router.patch("/{id}/status", response_model=ComplaintResponse)
def update_complaint_status(id: UUID, complaint_update: ComplaintUpdate, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = complaint_update.status
    db.commit()
    db.refresh(complaint)
    return complaint

@router.post("/{id}/notes")
def add_complaint_note(id: UUID, note: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Placeholder logic for adding a note
    return {"message": "Note added successfully", "note": note}
