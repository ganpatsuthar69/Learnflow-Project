from pydantic import BaseModel
from uuid import UUID
from datetime import datetime, date
from typing import Optional

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str
    topic: Optional[str] = None
    priority: Optional[str] = "medium"
    planned_date: date
    estimated_time: Optional[float] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    planned_date: Optional[date] = None
    estimated_time: Optional[float] = None

class TaskResponse(TaskBase):
    id: UUID
    status: str
    is_carried_forward: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
