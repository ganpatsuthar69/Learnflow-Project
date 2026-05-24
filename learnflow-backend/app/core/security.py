# hash+jwt
#password hash logic
#otp generation and send otp

import smtplib
import ssl
from email.message import EmailMessage
from passlib.context import CryptContext # type: ignore
from jose import jwt, JWTError # type: ignore
from datetime import datetime, timedelta
from .config import settings
import secrets, hashlib
from datetime import datetime, timedelta
from app.core.config import *

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



def send_email_otp(to_email: str, otp: str):
    smtp_server = settings.MAIL_SERVER
    smtp_port = settings.MAIL_PORT
    smtp_user = settings.MAIL_USERNAME
    smtp_password = settings.MAIL_PASSWORD

    message = EmailMessage()
    message["From"] = f"LearnFlow <{settings.MAIL_FROM}>"
    message["Reply-To"] = settings.MAIL_FROM
    message["To"] = to_email
    message["Subject"] = "Your OTP - LearnFlow"

    message.set_content(f"""
                            Hi,

                            Your OTP for LearnFlow is: {otp}

                            This OTP is valid for 5 minutes.

                            If you did not request this, please ignore this email.

                            - LearnFlow Team
                            """)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.send_message(message)

        print("Email sent successfully")

    except Exception as e:
        print("Email sending failed:", str(e))