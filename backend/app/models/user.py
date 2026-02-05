from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Date, Integer 
from sqlalchemy.orm import relationship # type: ignore
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID # type: ignore
from ..db.base import Base


#user database model
class Student(Base):
    __tablename__ = "students"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile_no = Column(String, nullable = False)
    full_name = Column(String, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)

    user_roadmaps = relationship(
        "UserRoadmap",
        back_populates="student",
        cascade="all, delete")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    ) #this is same as Student Table Column "id"

    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=False)

    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)

    profile_photo_url = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EducationalDetail(Base):
    __tablename__ = "educational_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        unique=True,
        nullable=False
    ) #this is same as Student Table Column "id" and same as Profile Table Column "student_id"

    current_level = Column(String, nullable=True)      # school / college / employee
    course_type = Column(String, nullable=True)        # school / graduation / pg / other
    course_name = Column(String, nullable=True)        # BCA, MCA, 12th Science

    course_start_year = Column(Integer, nullable=True)
    course_end_year = Column(Integer, nullable=True)
    current_year = Column(Integer, nullable=True)

    institution_name = Column(String, nullable=True)   # college / school / company

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
