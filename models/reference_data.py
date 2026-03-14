"""Reference data models for states and DISCOMs."""

from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from config.database import Base


class State(Base):
    """Master list of Indian states used in filtering and configuration."""

    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)


class Discom(Base):
    """Electricity distribution companies associated with states."""

    __tablename__ = "discoms"
    __table_args__ = (UniqueConstraint("name", "state_id", name="uq_discom_name_state"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False, index=True)

