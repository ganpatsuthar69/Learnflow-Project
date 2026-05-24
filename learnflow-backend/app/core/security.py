import ssl
from email.message import EmailMessage
from passlib.context import CryptContext  # type: ignore
from jose import jwt, JWTError  # type: ignore
from datetime import datetime, timedelta
from .config import settings
import secrets
import hashlib
import aiosmtplib

pwd_ctx = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def verify_password(plain_pass: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain_pass, hashed)


def create_access_token(data: dict, expires_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def token_decode(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# OTP utilities

def generate_otp(length=6):
    return ''.join(secrets.choice("0123456789") for _ in range(length))


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


def otp_expiry(minutes):
    return datetime.utcnow() + timedelta(minutes=minutes)


def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    return hashlib.sha256(plain_otp.encode()).hexdigest() == hashed_otp


async def send_email_otp(to_email: str, otp: str):
    """Send OTP email asynchronously using aiosmtplib."""
    message = EmailMessage()
    message["From"] = f"LearnFlow <{settings.MAIL_FROM}>"
    message["Reply-To"] = settings.MAIL_FROM
    message["To"] = to_email
    message["Subject"] = "Your OTP - LearnFlow"

    message.set_content(
        f"Hi,\n\n"
        f"Your OTP for LearnFlow is: {otp}\n\n"
        f"This OTP is valid for 5 minutes.\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"- LearnFlow Team"
    )

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.MAIL_SERVER,
            port=settings.MAIL_PORT,
            username=settings.MAIL_USERNAME,
            password=settings.MAIL_PASSWORD,
            start_tls=True,
        )
        print("Email sent successfully")
    except Exception as e:
        print(f"Email sending failed: {e}")
