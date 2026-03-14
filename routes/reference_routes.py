"""Reference data APIs for state and DISCOM lookups."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from models.reference_data import Discom, State
from schemas.reference_schema import DiscomResponse, StateResponse
from utils.dependencies import get_db

reference_router = APIRouter(prefix="/api", tags=["Reference Data"])
router = reference_router


@reference_router.get("/states", response_model=List[StateResponse])
def list_states(db: Session = Depends(get_db)):
    """Return all states sorted by name for dropdown usage."""
    return db.query(State).order_by(State.name.asc()).all()


@reference_router.get("/discoms", response_model=List[DiscomResponse])
def list_discoms(
    state_id: Optional[int] = Query(default=None, ge=1),
    db: Session = Depends(get_db),
):
    """Return DISCOMs, optionally filtered by state_id."""
    query = db.query(Discom, State.name.label("state_name")).join(State, State.id == Discom.state_id)
    if state_id is not None:
        query = query.filter(Discom.state_id == state_id)

    rows = query.order_by(Discom.name.asc()).all()
    return [
        DiscomResponse(id=discom.id, name=discom.name, state=state_name)
        for discom, state_name in rows
    ]
