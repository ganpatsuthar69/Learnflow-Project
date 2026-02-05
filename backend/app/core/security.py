# hash+jwt
#password hash logic
#otp generation and send otp

from passlib.context import CryptContext # type: ignore
from jose import jwt, JWTError # type: ignore
from datetime import datetime, timedelta
from .config import settings
import secrets, hashlib
from datetime import datetime, timedelta
import smtplib
from app.core.config import *
import ssl
from email.message import EmailMessage

pwd_ctx = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain_pass: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain_pass, hashed)

def create_access_token(data:dict, expires_minutes: int=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM )
    return token

def token_decode(token:str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = [settings.ALGORITHM])
        return payload
    except: 
        return None

#OTP

def generate_otp(length=6):
    return ''.join(secrets.choice("0123456789") for _ in range(length))  # "348102"

def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()

def otp_expiry(minutes):
    return datetime.utcnow() + timedelta(minutes=minutes)

def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    return hashlib.sha256(plain_otp.encode()).hexdigest() == hashed_otp


def send_email_otp(to_email, otp):
    smtp_server = "smtp.sendgrid.net"
    smtp_port = 587
    smtp_user = "apikey"
    smtp_password = settings.smtp_password #from sendgrid , created api

    message = EmailMessage()
    message["From"] = "LearnFlow <bheruji71@gmail.com>"
    message["Reply-To"] = "bheruji71@gmail.com"  
    message["To"] = to_email
    message["Subject"] = "Your OTP"
    message.set_content(f"Your OTP for Learnflow is: {otp}")

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_password)
        server.send_message(message)