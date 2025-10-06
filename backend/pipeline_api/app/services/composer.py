from sqlalchemy.orm import Session
from app.models.entry import Entry

def post_entry(db: Session, raw_text: str, source: str = "text") -> int:
    ent = Entry(raw_text=raw_text, source=source, status="posted")
    db.add(ent)
    db.commit()
    db.refresh(ent)
    return ent.id
