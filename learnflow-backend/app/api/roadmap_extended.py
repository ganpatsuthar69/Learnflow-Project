from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from ..db.session import get_db
from ..models.roadmap import Roadmap, Step, Topic
from ..schema.roadmap_extended import (
    RoadmapCreate, 
    RoadmapExtendedResponse, 
    StepCreate, 
    TopicCreate)

router = APIRouter()

@router.post("/roadmaps/extended", response_model=RoadmapExtendedResponse)
def create_roadmap_extended(roadmap_in: RoadmapCreate, db: Session = Depends(get_db)):
    # Create Roadmap
    db_roadmap = Roadmap(
        title=roadmap_in.title,
        description=roadmap_in.description,
        level=roadmap_in.level,
        roadmap_type=roadmap_in.roadmap_type,
        created_by_ai=roadmap_in.created_by_ai
    )
    db.add(db_roadmap)
    db.commit()
    db.refresh(db_roadmap)

    # Create Nested Steps and Topics if provided
    if roadmap_in.steps:
        for step_in in roadmap_in.steps:
            db_step = Step(
                roadmap_id=db_roadmap.id,
                title=step_in.title,
                description=step_in.description,
                step_order=step_in.step_order
            )
            db.add(db_step)
            db.commit()
            db.refresh(db_step)

            if step_in.topics:
                for topic_in in step_in.topics:
                    db_topic = Topic(
                        step_id=db_step.id,
                        title=topic_in.title,
                        description=topic_in.description,
                        topic_order=topic_in.topic_order
                    )
                    db.add(db_topic)
        
        db.commit()
        db.refresh(db_roadmap)

    return db_roadmap

@router.get("/roadmaps/{roadmap_id}/extended", response_model=RoadmapExtendedResponse)
def get_roadmap_extended(roadmap_id: UUID, db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    return roadmap

@router.post("/roadmaps/{roadmap_id}/steps", response_model=RoadmapExtendedResponse)
def add_step_to_roadmap(roadmap_id: UUID, step_in: StepCreate, db: Session = Depends(get_db)):
    roadmap = db.query(Roadmap).filter(Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Roadmap not found")
    
    db_step = Step(
        roadmap_id=roadmap_id,
        title=step_in.title,
        description=step_in.description,
        step_order=step_in.step_order
    )
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    
    # Handle nested topics in the new step
    if step_in.topics:
        for topic_in in step_in.topics:
            db_topic = Topic(
                step_id=db_step.id,
                title=topic_in.title,
                description=topic_in.description,
                topic_order=topic_in.topic_order
            )
            db.add(db_topic)
        db.commit()
    
    db.refresh(roadmap)
    return roadmap
