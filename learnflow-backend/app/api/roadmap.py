from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.roadmap import Roadmap
from app.db.session import get_db
from app.schema.roadmap import RoadmapResponse
from uuid import UUID

router = APIRouter()


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
