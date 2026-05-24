from fastapi import Depends, HTTPException, status, BackgroundTasks, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.models.user import Student, Profile
from app.models.verification import Verification, PasswordResetOTP
from app.schema.user import Student_login, Student_Signup
from app.schema.jwt_and_otp import TokenResponse, VerifyOTP, ResetPassword, ForgotPassword
from app.core.security import (
    hash_password, verify_password, create_access_token,
    generate_otp, hash_otp, otp_expiry, verify_otp, send_email_otp,
)
from app.services.queue_client import send_email
from datetime import datetime

router = APIRouter()

# Constants
MAX_OTP_ATTEMPTS = 5
OTP_SIGNUP_EXPIRY_MINUTES = 2
OTP_RESET_EXPIRY_MINUTES = 10


@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
async def sign_up_form(
    student_signup: Student_Signup,
    background_tsks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Register a new student and send OTP for email verification."""
    result = await db.execute(
        select(Student).filter(Student.email == student_signup.email)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or Mobile Number already registered",
        )

    result = await db.execute(
        select(Student).filter(Student.username == student_signup.username)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username already exists",
        )

    now = datetime.utcnow()

    # Check for existing verification with row lock
    result = await db.execute(
        select(Verification)
        .filter(Verification.email == student_signup.email)
        .with_for_update()
    )
    existv = result.scalars().first()

    if existv:
        if existv.expires_at and existv.expires_at > now:
            remaining_seconds = int((existv.expires_at - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"OTP already sent. Please wait {remaining_seconds} seconds",
            )
        else:
            await db.delete(existv)
            await db.commit()

    # Generate OTP and create verification record
    otp = generate_otp()
    otp_hash = hash_otp(otp)

    user_st = Verification(
        full_name=student_signup.full_name,
        email=student_signup.email,
        username=student_signup.username,
        mobile_no=student_signup.mobile_no,
        code=otp_hash,
        hashed_password=hash_password(student_signup.password),
        expires_at=otp_expiry(OTP_SIGNUP_EXPIRY_MINUTES),
        otp_attempts=0,
    )

    try:
        db.add(user_st)
        await db.commit()
        await db.refresh(user_st)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create verification. Please try again.",
        )

    background_tsks.add_task(send_email_otp, student_signup.email, otp)
    # Also queue via Lambda for reliability
    try:
        send_email(student_signup.email, "otp", {"otp": otp})
    except Exception:
        pass  # Fallback: background task still sends directly
    return {"msg": "OTP sent to your email. Verify to complete signup."}


@router.post("/sign_up/verify", status_code=status.HTTP_200_OK)
async def verify_user_by_email(
    otp_verify: VerifyOTP,
    db: AsyncSession = Depends(get_db),
):
    """Verify email with OTP and complete user registration."""
    result = await db.execute(
        select(Verification)
        .filter(Verification.email == otp_verify.email)
        .with_for_update()
    )
    v = result.scalars().first()

    if not v:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    now = datetime.utcnow()

    if v.expires_at is None or v.expires_at < now:
        await db.delete(v)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please sign up again",
        )

    if v.otp_attempts >= MAX_OTP_ATTEMPTS:
        await db.delete(v)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please sign up again",
        )

    if not verify_otp(otp_verify.otp, v.code):
        v.otp_attempts = (v.otp_attempts or 0) + 1
        await db.commit()
        remaining_attempts = MAX_OTP_ATTEMPTS - v.otp_attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {remaining_attempts} attempts remaining",
        )

    # Check if user already exists
    result = await db.execute(
        select(Student).filter(Student.email == v.email)
    )
    if result.scalars().first():
        await db.delete(v)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new student account
    user_ver = Student(
        full_name=v.full_name,
        email=v.email,
        mobile_no=v.mobile_no,
        username=v.username,
        hashed_password=v.hashed_password,
        is_active=True,
        is_verified=True,
    )
    try:
        db.add(user_ver)
        await db.delete(v)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification failed. Please try again.",
        )

    return {"msg": "Verification successful. You can now login"}


@router.post("/login", response_model=TokenResponse)
async def user_login(
    student_log_in: Student_login,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return access token."""
    result = await db.execute(
        select(Student).filter(Student.email == student_log_in.email)
    )
    user_exist = result.scalars().first()

    if not user_exist or not user_exist.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(student_log_in.password, user_exist.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user_exist.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in",
        )

    access_token = create_access_token(data={"sub": str(user_exist.id)})

    result = await db.execute(
        select(Profile).filter(Profile.student_id == user_exist.id)
    )
    profile = result.scalars().first()
    profile_completed = bool(profile)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        profile_completed=profile_completed,
    )


@router.post("/forgotpassword", status_code=status.HTTP_200_OK)
async def forgot_password(
    password_reset: ForgotPassword,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Send password reset OTP to user's email."""
    result = await db.execute(
        select(Student).filter(Student.email == password_reset.email)
    )
    user_exist = result.scalars().first()

    if not user_exist:
        return {"msg": "If the email exists, OTP has been sent"}

    now = datetime.utcnow()

    result = await db.execute(
        select(PasswordResetOTP).filter(PasswordResetOTP.email == password_reset.email)
    )
    existing_otp = result.scalars().first()

    if existing_otp:
        if existing_otp.expires_at and existing_otp.expires_at > now:
            remaining_seconds = int((existing_otp.expires_at - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"OTP already sent. Please wait {remaining_seconds} seconds",
            )
        else:
            await db.delete(existing_otp)
            await db.commit()

    otp = generate_otp()

    user_verification = PasswordResetOTP(
        email=password_reset.email,
        code=hash_otp(otp),
        expires_at=otp_expiry(OTP_RESET_EXPIRY_MINUTES),
        otp_attempts=0,
    )

    db.add(user_verification)
    await db.commit()

    background_tasks.add_task(send_email_otp, password_reset.email, otp)
    # Also queue via Lambda for reliability
    try:
        send_email(password_reset.email, "otp", {"otp": otp})
    except Exception:
        pass
    return {"msg": "OTP sent to your email"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    data: ResetPassword,
    db: AsyncSession = Depends(get_db),
):
    """Reset user password using OTP verification."""
    result = await db.execute(
        select(PasswordResetOTP)
        .filter(PasswordResetOTP.email == data.email)
        .with_for_update()
    )
    verification = result.scalars().first()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    if verification.expires_at < datetime.utcnow():
        await db.delete(verification)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please request a new one",
        )

    if verification.otp_attempts >= MAX_OTP_ATTEMPTS:
        await db.delete(verification)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please request a new OTP",
        )

    if not verify_otp(data.otp, verification.code):
        verification.otp_attempts += 1
        await db.commit()
        remaining_attempts = MAX_OTP_ATTEMPTS - verification.otp_attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {remaining_attempts} attempts remaining",
        )

    result = await db.execute(
        select(Student).filter(Student.email == data.email)
    )
    user = result.scalars().first()

    if not user:
        await db.delete(verification)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.hashed_password = hash_password(data.new_password)
    await db.delete(verification)
    await db.commit()

    return {"msg": "Password reset successful"}
