from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.entries import EntryDraft, EntryPosted
from app.services.composer import post_entry

router = APIRouter()

@router.post("/entries", response_model=EntryPosted)
def create_entry(payload: EntryDraft, db: Session = Depends(get_db)):
    new_id = post_entry(db, payload.text, payload.source)
    return EntryPosted(entry_id=new_id, status="posted")
