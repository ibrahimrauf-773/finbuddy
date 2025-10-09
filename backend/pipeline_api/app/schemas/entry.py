from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import date


class EntryCreate(BaseModel):
    occurred_on: date
    activity: str
    amount_cents: int
    currency: str
    notes: Optional[str] = None

class EntryOut(BaseModel):
    id: int
    occurred_on: date
    activity: str
    amount_cents: int
    currency: str
    notes: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)