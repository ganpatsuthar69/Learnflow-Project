from typing import Optional
from pydantic import BaseModel, EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile_completed: bool

class VerifyOTP(BaseModel):
    email: EmailStr 
    mobile_no: Optional[int] = None
    otp: str
    
class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

