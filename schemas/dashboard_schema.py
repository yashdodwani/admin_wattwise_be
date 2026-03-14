"""Pydantic schemas for dashboard analytics endpoints."""

from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    total_users: int
    active_meters: int
    total_revenue: float
    total_complaints: int
    overdue_bills: int
    recharge_volume: int


class ComplaintStatusCount(BaseModel):
    status: str
    count: int

