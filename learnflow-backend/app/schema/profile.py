from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import date
from pydantic import model_validator

class ProfileSchema(BaseModel):
     gender: str
     city : str
     state: str
     country :str 
     profile_photo_url:Optional[str] = None
     date_of_birth : date

     @model_validator(mode="after")
     def validate_dob(self):
        if self.date_of_birth > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return self

class EducationalDetailsSchema(BaseModel):
    current_level: Optional[str]        # school / college / employee
    course_type: Optional[str]          # school / graduation / pg / other
    course_name: Optional[str]          # BCA, MCA, 12th Science

    course_start_year: Optional[int]
    course_end_year: Optional[int]
    current_year: Optional[int]
    institution_name: Optional[str]     # college / school / company

    @model_validator(mode="after")
    def validate_years(self):
        if self.course_start_year and self.course_end_year:
            if self.course_end_year < self.course_start_year:
                raise ValueError("course_end_year cannot be before course_start_year")
        return self

class ProfileCreate(BaseModel):
    profile: ProfileSchema
    education: EducationalDetailsSchema


class ProfileUpdate(BaseModel):
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    profile_photo_url: Optional[str] = None


class EducationalDetailsUpdate(BaseModel):
    current_level: Optional[str] = None
    course_type: Optional[str] = None
    course_name: Optional[str] = None
    course_start_year: Optional[int] = None
    course_end_year: Optional[int] = None
    current_year: Optional[int] = None
    institution_name: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    profile: Optional[ProfileUpdate] = None
    education: Optional[EducationalDetailsUpdate] = None

class EmailUpdate(BaseModel):
    email : Optional[EmailStr]

class ProfileOutput(BaseModel):
    # Student table
    full_name: str
    username: str
    email: str
    # Profile table
    date_of_birth: date
    gender: str
    city: str
    state: str
    country: str
    profile_photo_url: Optional[str]
    # EducationalDetails table
    current_level: Optional[str]
    course_type: Optional[str]
    course_name: Optional[str]
    course_start_year: Optional[int]
    course_end_year: Optional[int]
    current_year: Optional[int]
    institution_name: Optional[str]

    class Config:
        from_attributes = True