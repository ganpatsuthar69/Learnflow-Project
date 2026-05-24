from typing import Optional
from pydantic import BaseModel, EmailStr

#user registration pydantic models
class Student_Signup(BaseModel):
    full_name : Optional[str]
    password : str
    username: str
    email  : EmailStr
    mobile_no : str
class Student_login(BaseModel):
    email: str
    password : str
