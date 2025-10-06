from pydantic import BaseModel, Field

class EntryDraft(BaseModel):
    text: str = Field(..., min_length=1)
    source: str = "text"

class EntryPosted(BaseModel):
    entry_id: int
    status: str
