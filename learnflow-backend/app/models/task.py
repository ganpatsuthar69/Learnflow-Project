from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Date, Float, Enum
from sqlalchemy.dialects.postgresql import UUID # type: ignore
from ..db.base import Base
from datetime import datetime
import uuid

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    
    status = Column(String, default="pending") # "pending", "completed", "missed"
    priority = Column(String, default="medium") # "high", "medium", "low"
    
    planned_date = Column(Date, nullable=False)
    estimated_time = Column(Float, nullable=True) # in hours
    
    is_carried_forward = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
