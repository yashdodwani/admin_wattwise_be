"""Pydantic schemas for reference data APIs."""

from pydantic import BaseModel


class StateResponse(BaseModel):
    id: int
    name: str


class DiscomResponse(BaseModel):
    id: int
    name: str
    state: str

