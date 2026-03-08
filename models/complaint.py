from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from enum import Enum as PyEnum

Base = declarative_base()

class Priority(PyEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class Status(PyEnum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"

class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complaint_id = Column(String, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    issue_type = Column(String, nullable=False)
    priority = Column(Enum(Priority), nullable=False)
    status = Column(Enum(Status), nullable=False)
    agent_name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
