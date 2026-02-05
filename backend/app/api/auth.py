from fastapi import Depends, HTTPException, status, BackgroundTasks, APIRouter
from sqlalchemy.orm import Session  # type: ignore
from app.db.session import get_db
from app.models.user import Student
from app.models.verification import Verification, PasswordResetOTP
from app.schema.user import Student_login, Student_Signup
from app.schema.jwt_and_otp import TokenResponse, VerifyOTP, ResetPassword, ForgotPassword
from sqlalchemy import or_  # type: ignore
from app.core.security import *
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from app.models.user import Profile

router = APIRouter()

# Constants
MAX_OTP_ATTEMPTS = 5
OTP_SIGNUP_EXPIRY_MINUTES = 2
OTP_RESET_EXPIRY_MINUTES = 5


@router.post("/sign_up", status_code=status.HTTP_201_CREATED)
def sign_up_form(
    student_signup: Student_Signup,
    background_tsks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Register a new student and send OTP for email verification.
    """
    # Check if email or mobile number already exists
    exist = db.query(Student).filter(Student.email == student_signup.email).first()

    if exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or Mobile Number already registered",
        )

    # Check if username already exists
    exist_username = db.query(Student).filter(
        Student.username == student_signup.username
    ).first()
    
    if exist_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username already exists",
        )

    now = datetime.utcnow()
    
    # Check for existing verification with row lock
    existv = (
        db.query(Verification)
        .filter(Verification.email == student_signup.email)
        .with_for_update()
        .first()
    )

    if existv:
        if existv.expires_at and existv.expires_at > now:
            remaining_seconds = int((existv.expires_at - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"OTP already sent. Please wait {remaining_seconds} seconds",
            )
        else:
            db.delete(existv)
            db.commit()

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
        db.commit()
        db.refresh(user_st)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create verification. Please try again.",
        )

    background_tsks.add_task(send_email_otp, student_signup.email, otp)
    return {"msg": "OTP sent to your email. Verify to complete signup."}


@router.post("/sign_up/verify", status_code=status.HTTP_200_OK)
def verify_user_by_email(otp_verify: VerifyOTP, db: Session = Depends(get_db)):
    """
    Verify email with OTP and complete user registration.
    """
    # Lock the verification record to prevent race conditions
    v = (
        db.query(Verification)
        .filter(Verification.email == otp_verify.email)
        .with_for_update()
        .first()
    )

    if not v:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    now = datetime.utcnow()

    # Check if OTP has expired
    if v.expires_at is None or v.expires_at < now:
        db.delete(v)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please sign up again",
        )

    # Check if maximum attempts exceeded
    if v.otp_attempts >= MAX_OTP_ATTEMPTS:
        db.delete(v)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please sign up again",
        )

    # Verify OTP
    if not verify_otp(otp_verify.otp, v.code):
        v.otp_attempts = (v.otp_attempts or 0) + 1
        db.commit()
        
        remaining_attempts = MAX_OTP_ATTEMPTS - v.otp_attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {remaining_attempts} attempts remaining",
        )

    # Check if user already exists
    if db.query(Student).filter(Student.email == v.email).first():
        db.delete(v)
        db.commit()
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
        is_verified=True)
    try:
        db.add(user_ver)
        db.delete(v)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification failed. Please try again.",
        )

    return {"msg": "Verification successful. You can now login"}


@router.post("/login", response_model=TokenResponse)
def user_login(student_log_in: Student_login, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    """
    user_exist = db.query(Student).filter(
        Student.email == student_log_in.email
    ).first()

    # Check if user exists and is active
    if not user_exist or not user_exist.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials")

    # Verify password
    if not verify_password(student_log_in.password, user_exist.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    # Check if user is verified
    if not user_exist.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in")

    # Generate access token
    access_token = create_access_token(data={"sub": str(user_exist.id)})
    profile = (db.query(Profile).filter(Profile.student_id == user_exist.id).first())
    profile_completed = bool(profile)
    return TokenResponse(access_token=access_token, token_type="bearer", profile_completed=profile_completed)


@router.post("/forgotpassword", status_code=status.HTTP_200_OK)
def forgot_password(
    password_reset: ForgotPassword,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Send password reset OTP to user's email.
    """
    user_exist = db.query(Student).filter(
        Student.email == password_reset.email
    ).first()

    # Return generic message to prevent email enumeration
    if not user_exist:
        return {"msg": "If the email exists, OTP has been sent"}

    now = datetime.utcnow()
    
    # Check for existing password reset OTP
    existing_otp = (
        db.query(PasswordResetOTP)
        .filter(PasswordResetOTP.email == password_reset.email)
        .first()
    )

    if existing_otp:
        if existing_otp.expires_at and existing_otp.expires_at > now:
            remaining_seconds = int((existing_otp.expires_at - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"OTP already sent. Please wait {remaining_seconds} seconds",
            )
        else:
            db.delete(existing_otp)
            db.commit()

    # Generate new OTP
    otp = generate_otp()

    user_verification = PasswordResetOTP(
        email=password_reset.email,
        code=hash_otp(otp),
        expires_at=otp_expiry(OTP_RESET_EXPIRY_MINUTES),
        otp_attempts=0,
    )

    db.add(user_verification)
    db.commit()

    background_tasks.add_task(send_email_otp, password_reset.email, otp)
    return {"msg": "OTP sent to your email"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    """
    Reset user password using OTP verification.
    """
    # Lock the verification record to prevent race conditions
    verification = (
        db.query(PasswordResetOTP)
        .filter(PasswordResetOTP.email == data.email)
        .with_for_update()
        .first()
    )

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    # Check if OTP has expired
    if verification.expires_at < datetime.utcnow():
        db.delete(verification)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please request a new one",
        )

    # Check if maximum attempts exceeded
    if verification.otp_attempts >= MAX_OTP_ATTEMPTS:
        db.delete(verification)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please request a new OTP",
        )

    # Verify OTP
    if not verify_otp(data.otp, verification.code):
        verification.otp_attempts += 1
        db.commit()
        
        remaining_attempts = MAX_OTP_ATTEMPTS - verification.otp_attempts
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {remaining_attempts} attempts remaining",
        )

    # Find user and update password
    user = db.query(Student).filter(Student.email == data.email).first()

    if not user:
        db.delete(verification)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.hashed_password = hash_password(data.new_password)
    db.delete(verification)
    db.commit()

    return {"msg": "Password reset successful"}