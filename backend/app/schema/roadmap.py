# schemas/roadmap.py
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class RoadmapResponse(BaseModel):
    id : UUID
    title: str
    description: Optional[str]
    level: Optional[str]

    class Config:
        from_attributes = True

class RoadmapRequest(BaseModel):
    id : UUID
    title : Optional[str]
    description : Optional[str]
    level : Optional[str]

class RoadmapRequestResponse(BaseModel):
    id : UUID
    title : Optional[str]
    description : Optional[str]
    level : Optional[str]
    