from sqlalchemy import Column, Integer, String, DateTime, Boolean # type: ignore
from sqlalchemy.dialects.postgresql import UUID # type: ignore
import uuid
from datetime import datetime
from ..db.base import Base

class Verification(Base):
    __tablename__ = "verifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    email = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    mobile_no = Column(String, nullable=True)
    code = Column(String, nullable=False) #otp code
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    otp_attempts = Column(Integer,nullable = False,  default= 0)

    
class PasswordResetOTP(Base):
    __tablename__ = "password_reset_otps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    otp_attempts = Column(Integer, default=0)

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class EmailChangeRequest(Base):
    __tablename__ = "email_change_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(
        UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,)

    new_email = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    otp_attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
