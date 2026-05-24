from datetime import datetime
from fastapi import Depends, HTTPException, status, APIRouter, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.models.verification import EmailChangeRequest
from app.models.user import Profile, EducationalDetail, Student
from app.db.session import get_db
from app.api.deps import get_current_user
from app.schema.profile import ProfileOutput, ProfileCreate, ProfileUpdateRequest, EmailUpdate
from app.schema.jwt_and_otp import VerifyOTP
from app.core.security import generate_otp, hash_otp, otp_expiry, verify_otp, send_email_otp
import os
import httpx

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


@router.get("/profile", response_model=ProfileOutput)
async def get_profile(
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the current user's profile and educational details."""
    result = await db.execute(
        select(Profile).filter(Profile.student_id == current_user.id)
    )
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create your profile first",
        )

    result = await db.execute(
        select(EducationalDetail).filter(EducationalDetail.student_id == current_user.id)
    )
    education = result.scalars().first()

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
async def post_profile(
    data: ProfileCreate,
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new profile and educational details for the current user."""
    result = await db.execute(
        select(Profile).filter(Profile.student_id == current_user.id)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists. Use the update endpoint to modify it",
        )

    profile_add = Profile(
        student_id=current_user.id,
        date_of_birth=data.profile.date_of_birth,
        gender=data.profile.gender,
        city=data.profile.city,
        state=data.profile.state,
        country=data.profile.country,
        profile_photo_url=None,
    )

    education_add = EducationalDetail(
        student_id=current_user.id,
        current_level=data.education.current_level,
        course_type=data.education.course_type,
        course_name=data.education.course_name,
        course_start_year=data.education.course_start_year,
        course_end_year=data.education.course_end_year,
        current_year=data.education.current_year,
        institution_name=data.education.institution_name,
    )

    try:
        db.add(profile_add)
        db.add(education_add)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists",
        )
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile creation failed",
        )

    return {"msg": "Profile created successfully"}


@router.patch("/profile_update", status_code=status.HTTP_200_OK)
async def update_profile(
    data: ProfileUpdateRequest,
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile and/or educational details."""
    if not data.profile and not data.education:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided",
        )

    result = await db.execute(
        select(Profile).filter(Profile.student_id == current_user.id)
    )
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create your profile first",
        )

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

    if data.education:
        result = await db.execute(
            select(EducationalDetail).filter(
                EducationalDetail.student_id == current_user.id
            )
        )
        education = result.scalars().first()

        if education:
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
            education = EducationalDetail(
                student_id=current_user.id,
                current_level=data.education.current_level,
                course_type=data.education.course_type,
                course_name=data.education.course_name,
                course_start_year=data.education.course_start_year,
                course_end_year=data.education.course_end_year,
                current_year=data.education.current_year,
                institution_name=data.education.institution_name,
            )
            db.add(education)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile update failed. Please try again",
        )

    return {"msg": "Profile updated successfully"}


# --- Profile Photo Endpoints (async Supabase Storage via httpx) ---

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}
ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@router.post("/profile/photo", status_code=status.HTTP_200_OK)
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG and PNG images are allowed")

    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid image file extension")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image size must be less than 5MB")

    result = await db.execute(
        select(Profile).filter(Profile.student_id == current_user.id)
    )
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create profile first")

    file_path = f"avatars/{current_user.id}.jpg"

    async with httpx.AsyncClient() as client:
        upload_url = f"{SUPABASE_URL}/storage/v1/object/Profiles/{file_path}"
        resp = await client.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": file.content_type,
                "x-upsert": "true",
            },
            content=contents,
        )
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=500, detail="Failed to upload profile photo")

    profile.profile_photo_url = file_path
    await db.commit()
    return {"msg": "Profile photo uploaded successfully"}


@router.get("/profile/photo", status_code=status.HTTP_200_OK)
async def get_profile_photo(
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Profile).filter(Profile.student_id == current_user.id)
    )
    profile = result.scalars().first()

    if not profile or not profile.profile_photo_url:
        raise HTTPException(status_code=404, detail="Profile photo not found")

    async with httpx.AsyncClient() as client:
        sign_url = f"{SUPABASE_URL}/storage/v1/object/sign/Profiles/{profile.profile_photo_url}"
        resp = await client.post(
            sign_url,
            headers={"Authorization": f"Bearer {SUPABASE_KEY}"},
            json={"expiresIn": 600},
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to generate signed URL")
        data = resp.json()

    return {"url": f"{SUPABASE_URL}/storage/v1{data['signedURL']}"}


@router.delete("/profile/photo", status_code=status.HTTP_200_OK)
async def delete_profile_photo(
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Profile).filter(Profile.student_id == current_user.id)
    )
    profile = result.scalars().first()

    if not profile or not profile.profile_photo_url:
        raise HTTPException(status_code=404, detail="Profile photo not found")

    async with httpx.AsyncClient() as client:
        delete_url = f"{SUPABASE_URL}/storage/v1/object/Profiles"
        resp = await client.delete(
            delete_url,
            headers={"Authorization": f"Bearer {SUPABASE_KEY}"},
            json={"prefixes": [profile.profile_photo_url]},
        )
        if resp.status_code not in (200, 204):
            raise HTTPException(status_code=500, detail="Failed to delete profile photo")

    profile.profile_photo_url = None
    await db.commit()
    return {"msg": "Profile photo deleted successfully"}


# --- Email Change Endpoints ---

@router.patch("/profile/email/request", status_code=200)
async def request_email_change(
    data: EmailUpdate,
    background_tasks: BackgroundTasks,
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.email == current_user.email:
        raise HTTPException(400, "New email must be different")

    result = await db.execute(
        select(Student).filter(Student.email == data.email)
    )
    if result.scalars().first():
        raise HTTPException(400, "Email already in use")

    # Delete old requests
    result = await db.execute(
        select(EmailChangeRequest).filter(
            EmailChangeRequest.student_id == current_user.id
        )
    )
    old_requests = result.scalars().all()
    for req in old_requests:
        await db.delete(req)
    await db.commit()

    otp = generate_otp()
    otp_hash = hash_otp(otp)

    req = EmailChangeRequest(
        student_id=current_user.id,
        new_email=data.email,
        code=otp_hash,
        expires_at=otp_expiry(5),
    )

    db.add(req)
    await db.commit()

    background_tasks.add_task(send_email_otp, data.email, otp)
    return {"msg": "OTP sent to new email"}


@router.post("/profile/email/verify", status_code=200)
async def verify_email_change(
    data: VerifyOTP,
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EmailChangeRequest)
        .filter(
            EmailChangeRequest.student_id == current_user.id,
            EmailChangeRequest.new_email == data.email,
        )
        .with_for_update()
    )
    v = result.scalars().first()

    if not v:
        raise HTTPException(400, "Invalid or expired OTP")

    if v.expires_at < datetime.utcnow():
        await db.delete(v)
        await db.commit()
        raise HTTPException(400, "OTP expired")

    if v.otp_attempts >= 5:
        await db.delete(v)
        await db.commit()
        raise HTTPException(429, "Too many attempts")

    if not verify_otp(data.otp, v.code):
        v.otp_attempts += 1
        await db.commit()
        raise HTTPException(400, "Invalid OTP")

    try:
        current_user.email = v.new_email
        current_user.is_verified = True
        await db.delete(v)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(400, "Email update failed")

    return {"msg": "Email updated successfully"}
