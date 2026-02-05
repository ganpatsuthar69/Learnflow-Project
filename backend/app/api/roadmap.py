from fastapi import APIRouter, Depends, HTTPException, status
from ..models.roadmap import *
from ..db.session import get_db
from ..schema.roadmap import *
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/roadmaps", response_model=list[RoadmapResponse])
def get_roadmaps(db: Session = Depends(get_db)):
    roadmaps = db.query(Roadmap).all()
    return roadmaps

@router.get("/roadmaps/{roadmap_id}", response_model=RoadmapResponse)
def get_roadmap_by_id(roadmap_id: UUID, db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    return roadmap