from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class NoteBase(BaseModel):
    title: str
    description: Optional[str] = None

class NoteCreate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: UUID
    file_url: str
    file_type: str
    created_at: datetime

    class Config:
        from_attributes = True
