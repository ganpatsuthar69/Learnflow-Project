from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..db.base import Base
from datetime import datetime
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from ..models.user import Student
import uuid

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(String)
    level = Column(String)
    roadmap_type = Column(String, nullable=False)  # static | ai
    created_by_ai = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    steps = relationship("Step", back_populates="roadmap", cascade="all, delete")
    user_roadmaps = relationship("UserRoadmap", back_populates="roadmap")

class Step(Base):
    __tablename__ = "steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roadmap_id = Column(UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(String)
    step_order = Column(Integer)

    roadmap = relationship("Roadmap", back_populates="steps")
    topics = relationship("Topic", back_populates="step", cascade="all, delete")

class Topic(Base):
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    step_id = Column(UUID(as_uuid=True), ForeignKey("steps.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(String)
    topic_order = Column(Integer)

    step = relationship("Step", back_populates="topics")
    user_topic_progress = relationship("UserTopicProgress", back_populates="topic")

class UserRoadmap(Base):
    __tablename__ = "user_roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"))
    roadmap_id = Column(UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="CASCADE"))

    progress_percentage = Column(Integer, default=0)
    status = Column(String, default="active")
    started_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    student = relationship("Student", back_populates="user_roadmaps")
    roadmap = relationship("Roadmap", back_populates="user_roadmaps")
    topic_progress = relationship("UserTopicProgress", back_populates="user_roadmap")

class UserTopicProgress(Base):
    __tablename__ = "user_topic_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_roadmap_id = Column(UUID(as_uuid=True), ForeignKey("user_roadmaps.id", ondelete="CASCADE"))
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"))

    is_completed = Column(Boolean, default=False)
    started_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    completed_at = Column(TIMESTAMP(timezone=True), nullable=True)

    user_roadmap = relationship("UserRoadmap", back_populates="topic_progress")
    topic = relationship("Topic", back_populates="user_topic_progress")
