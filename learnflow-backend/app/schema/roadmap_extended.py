from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional
from datetime import datetime

# --- Topic Schemas ---
class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    topic_order: Optional[int] = None

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    topic_order: Optional[int] = None

class TopicResponse(TopicBase):
    id: UUID
    step_id: UUID

    class Config:
        from_attributes = True

# --- Step Schemas ---
class StepBase(BaseModel):
    title: str
    description: Optional[str] = None
    step_order: Optional[int] = None

class StepCreate(StepBase):
    topics: Optional[List[TopicCreate]] = []

class StepUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    step_order: Optional[int] = None

class StepResponse(StepBase):
    id: UUID
    roadmap_id: UUID
    topics: List[TopicResponse] = []

    class Config:
        from_attributes = True

# --- Roadmap Schemas ---
class RoadmapBase(BaseModel):
    title: str
    description: Optional[str] = None
    level: Optional[str] = None
    roadmap_type: str # static | ai
    created_by_ai: Optional[bool] = False

class RoadmapCreate(RoadmapBase):
    steps: Optional[List[StepCreate]] = []

class RoadmapUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    roadmap_type: Optional[str] = None
    created_by_ai: Optional[bool] = None

class RoadmapExtendedResponse(RoadmapBase):
    id: UUID
    created_at: datetime
    steps: List[StepResponse] = []

    class Config:
        from_attributes = True
