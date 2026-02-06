from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID # type: ignore
from ..db.base import Base
from datetime import datetime
import uuid

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    file_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False) # "pdf", "image", "word", "ppt"
    
    created_at = Column(DateTime, default=datetime.utcnow)
