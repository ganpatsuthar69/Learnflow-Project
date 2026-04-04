# Centralize model imports so SQLAlchemy builds the mapper registry completely 
# whenever `app.models` is accessed, preventing relationship resolution errors.

from .user import Student, Profile, EducationalDetail
from .verification import Verification, PasswordResetOTP, EmailChangeRequest
from .task import Task
from .roadmap import Roadmap, Step, Topic, UserRoadmap, UserTopicProgress
from .note import Note