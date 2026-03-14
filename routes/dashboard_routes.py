"""Dashboard API routes for admin analytics widgets and charts."""

from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.complaint import Complaint
from models.transaction import Transaction
from models.user import User
from schemas.dashboard_schema import ComplaintStatusCount, DashboardStatsResponse
from utils.dependencies import get_db

dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
router = dashboard_router


@dashboard_router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Return overall dashboard statistics used by KPI cards."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_meters = (
        db.query(func.count(func.distinct(User.meter_id)))
        .filter(User.is_active.is_(True))
        .scalar()
        or 0
    )
    total_revenue = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.status == "Success")
        .scalar()
        or 0
    )
    total_complaints = db.query(func.count(Complaint.id)).scalar() or 0
    overdue_bills = (
        db.query(func.count(User.id))
        .filter(User.remaining_balance > 0)
        .scalar()
        or 0
    )
    recharge_volume = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.status == "Success")
        .scalar()
        or 0
    )

    return DashboardStatsResponse(
        total_users=total_users,
        active_meters=active_meters,
        total_revenue=float(total_revenue),
        total_complaints=total_complaints,
        overdue_bills=overdue_bills,
        recharge_volume=recharge_volume,
    )


@dashboard_router.get("/complaints-status", response_model=List[ComplaintStatusCount])
def get_complaint_status_distribution(db: Session = Depends(get_db)):
    """Return complaint counts grouped by normalized status for pie charts."""
    rows = (
        db.query(Complaint.status, func.count(Complaint.id).label("count"))
        .group_by(Complaint.status)
        .all()
    )

    normalized: Dict[str, int] = {
        "open": 0,
        "in_progress": 0,
        "resolved": 0,
        "rejected": 0,
    }

    for row in rows:
        raw_value = str(row.status.value if hasattr(row.status, "value") else row.status)
        key = raw_value.strip().lower().replace(" ", "_")
        if key in {"escalated", "rejected"}:
            key = "rejected"
        if key in normalized:
            normalized[key] += int(row._mapping["count"])

    return [ComplaintStatusCount(status=status, count=count) for status, count in normalized.items()]
