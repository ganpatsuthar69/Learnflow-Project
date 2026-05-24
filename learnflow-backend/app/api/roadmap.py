from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.roadmap import Roadmap
from app.db.session import get_db
from app.schema.roadmap import RoadmapResponse
from app.api.deps import get_current_user
from app.models.user import Student
from app.services.queue_client import trigger_roadmap_generation
from uuid import UUID
from pydantic import BaseModel

router = APIRouter()


class RoadmapGenerateRequest(BaseModel):
    topic: str
    level: str = "beginner"
    context: str = ""


@router.get("/roadmaps", response_model=list[RoadmapResponse])
async def get_roadmaps(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Roadmap))
    return result.scalars().all()


@router.get("/roadmaps/{roadmap_id}", response_model=RoadmapResponse)
async def get_roadmap_by_id(roadmap_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Roadmap).filter(Roadmap.id == roadmap_id)
    )
    roadmap = result.scalars().first()
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roadmap not found",
        )
    return roadmap


@router.post("/roadmaps/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_roadmap(
    data: RoadmapGenerateRequest,
    current_user: Student = Depends(get_current_user),
):
    """Trigger AI roadmap generation via Lambda. Results are stored async."""
    trigger_roadmap_generation(
        student_id=str(current_user.id),
        topic=data.topic,
        level=data.level,
        context=data.context or f"{current_user.full_name} - CS student",
    )
    return {"msg": "Roadmap generation started", "topic": data.topic}
