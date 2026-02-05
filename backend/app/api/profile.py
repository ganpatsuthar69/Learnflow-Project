from app.core.security import *
from datetime import datetime
from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.verification import Verification , EmailChangeRequest
from app.models.user import Profile, EducationalDetail, Student
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schema.profile import ProfileOutput, ProfileCreate, ProfileUpdateRequest, EmailUpdate
from app.schema.jwt_and_otp import VerifyOTP
from sqlalchemy.exc import IntegrityError
from app.core.supabase import supabase
import os

router = APIRouter()


@router.get("/profile", response_model=ProfileOutput)
def get_profile(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)):
    """
    Retrieve the current user's profile and educational details.
    """
    profile = db.query(Profile).filter(
        Profile.student_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create your profile first",
        )

    education = db.query(EducationalDetail).filter(
        EducationalDetail.student_id == current_user.id
    ).first()

    return ProfileOutput(
        full_name=current_user.full_name,
        username=current_user.username,
        email=current_user.email,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender,
        city=profile.city,
        state=profile.state,
        country=profile.country,
        profile_photo_url=profile.profile_photo_url,
        current_level=education.current_level if education else None,
        course_type=education.course_type if education else None,
        course_name=education.course_name if education else None,
        course_start_year=education.course_start_year if education else None,
        course_end_year=education.course_end_year if education else None,
        current_year=education.current_year if education else None,
        institution_name=education.institution_name if education else None,
    )

@router.post("/profile_create", status_code=status.HTTP_201_CREATED)
def post_profile(
    data: ProfileCreate,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new profile and educational details for the current user.
    """
    
    # Check if profile already exists
    existing_profile = db.query(Profile).filter(
        Profile.student_id == current_user.id
    ).first()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists. Use the update endpoint to modify it",
        )

    # Create both records
    profile_add = Profile(
        student_id=current_user.id,
        date_of_birth=data.profile.date_of_birth,
        gender=data.profile.gender,
        city=data.profile.city,
        state=data.profile.state,
        country=data.profile.country,
        profile_photo_url = None,  # Don't allow direct URL setting
    )
    
    education_add = EducationalDetail(
        student_id=current_user.id,
        current_level=data.education.current_level,
        course_type=data.education.course_type,
        course_name=data.education.course_name,
        course_start_year=data.education.course_start_year,
        course_end_year=data.education.course_end_year,
        current_year=data.education.current_year,
        institution_name=data.education.institution_name
    )

    try:
        db.add(profile_add)
        db.add(education_add)
        db.commit()
        
    except IntegrityError as e:
        db.rollback()
        # Check if it's a duplicate key error
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            print(e)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profile already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data provided"
        )
    except Exception as e:
        db.rollback()
        # Log the error but don't expose it
        print(f"Profile creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile creation failed"
        )

    return {"msg": "Profile created successfully"}

@router.patch("/profile_update", status_code=status.HTTP_200_OK)
def update_profile(
    data: ProfileUpdateRequest,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the current user's profile and/or educational details.
    """
    # Validate that at least one field is being updated
    if not data.profile and not data.education:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided",
        )

    # Fetch existing profile
    profile = db.query(Profile).filter(
        Profile.student_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create your profile first",
        )

    # Update profile fields
    if data.profile:
        if data.profile.date_of_birth is not None:
            profile.date_of_birth = data.profile.date_of_birth
        if data.profile.gender is not None:
            profile.gender = data.profile.gender
        if data.profile.city is not None:
            profile.city = data.profile.city
        if data.profile.state is not None:
            profile.state = data.profile.state
        if data.profile.country is not None:
            profile.country = data.profile.country
        if data.profile.profile_photo_url is not None:
            profile.profile_photo_url = data.profile.profile_photo_url

    # Update educational details
    if data.education:
        education = db.query(EducationalDetail).filter(
            EducationalDetail.student_id == current_user.id
        ).first()

        if education:
            # Update existing educational details
            if data.education.current_level is not None:
                education.current_level = data.education.current_level
            if data.education.course_type is not None:
                education.course_type = data.education.course_type
            if data.education.course_name is not None:
                education.course_name = data.education.course_name
            if data.education.course_start_year is not None:
                education.course_start_year = data.education.course_start_year
            if data.education.course_end_year is not None:
                education.course_end_year = data.education.course_end_year
            if data.education.current_year is not None:
                education.current_year = data.education.current_year
            if data.education.institution_name is not None:
                education.institution_name = data.education.institution_name
        else:
            # Create new educational details if they don't exist
            education = EducationalDetail(
                student_id=current_user.id,
                current_level=data.education.current_level,
                course_type=data.education.course_type,
                course_name=data.education.course_name,
                course_start_year=data.education.course_start_year,
                course_end_year=data.education.course_end_year,
                current_year=data.education.current_year,
                institution_name=data.education.institution_name)
            db.add(education)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile update failed. Please try again")
    return {"msg": "Profile updated successfully"}


MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png"}

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png"}

@router.post("/profile/photo", status_code=status.HTTP_200_OK)
def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)):
    # 🔹 Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed")

    # 🔹 Validate extension
    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file extension")

    # 🔹 Validate file size
    contents = file.file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image size must be less than 5MB")
    file.file.seek(0)

    # 🔹 Ensure profile exists
    profile = db.query(Profile).filter(
        Profile.student_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. Create profile first"
        )
    file_path = f"avatars/{current_user.id}.jpg"

    # 🔹 Upload to Supabase (upsert = update)
    try:
        supabase.storage.from_("Profiles").upload(
                    file_path,
                    contents,
                    {
                        "content-type": file.content_type,
                        "upsert": "true"
                    })

    except Exception as e:
            print("SUPABASE ERROR:", e)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )


    profile.profile_photo_url = file_path
    db.commit()
    return {"msg": "Profile photo uploaded successfully"}


@router.get("/profile/photo", status_code=status.HTTP_200_OK)
def get_profile_photo(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(
        Profile.student_id == current_user.id).first()

    if not profile or not profile.profile_photo_url:
        raise HTTPException(
            status_code=404,
            detail="Profile photo not found")

    try:
        signed = supabase.storage.from_("Profiles").create_signed_url(
            profile.profile_photo_url, 600)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=str(e))
    return {"url": signed["signedURL"]}


@router.delete("/profile/photo", status_code=status.HTTP_200_OK)
def delete_profile_photo(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(
        Profile.student_id == current_user.id).first()

    if not profile or not profile.profile_photo_url:
        raise HTTPException(
            status_code=404,
            detail="Profile photo not found")
    try:
        supabase.storage.from_("Profiles").remove(
            [profile.profile_photo_url])
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete profile photo")
    profile.profile_photo_url = None
    db.commit()
    return {"msg": "Profile photo deleted successfully"}

@router.patch("/profile/email/request", status_code=200)
def request_email_change(
    data: EmailUpdate,
    background_tasks: BackgroundTasks,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.email == current_user.email:
        raise HTTPException(400, "New email must be different")

    if db.query(Student).filter(Student.email == data.email).first():
        raise HTTPException(400, "Email already in use")

    # delete old requests
    db.query(EmailChangeRequest).filter(
        EmailChangeRequest.student_id == current_user.id
    ).delete()
    db.commit()

    otp = generate_otp()
    otp_hash = hash_otp(otp)

    req = EmailChangeRequest(
        student_id=current_user.id,
        new_email=data.email,
        code=otp_hash,
        expires_at=otp_expiry(5),
    )

    db.add(req)
    db.commit()

    background_tasks.add_task(send_email_otp, data.email, otp)

    return {"msg": "OTP sent to new email"}


@router.post("/profile/email/verify", status_code=200)
def verify_email_change(
    data: VerifyOTP,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    v = (
        db.query(EmailChangeRequest)
        .filter(
            EmailChangeRequest.student_id == current_user.id,
            EmailChangeRequest.new_email == data.email,
        )
        .with_for_update()
        .first()
    )

    if not v:
        raise HTTPException(400, "Invalid or expired OTP")

    if v.expires_at < datetime.utcnow():
        db.delete(v)
        db.commit()
        raise HTTPException(400, "OTP expired")

    if v.otp_attempts >= 5:
        db.delete(v)
        db.commit()
        raise HTTPException(429, "Too many attempts")

    if not verify_otp(data.otp, v.code):
        v.otp_attempts += 1
        db.commit()
        raise HTTPException(400, "Invalid OTP")

    try:
        # ✅ update email safely
        current_user.email = v.new_email
        current_user.is_verified = True

        # ✅ delete only the OTP request
        db.delete(v)
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(400, "Email update failed")

    return {"msg": "Email updated successfully"}
