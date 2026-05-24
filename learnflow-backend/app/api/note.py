from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import Student
from app.models.note import Note
from app.schema.note import NoteResponse
import os
import uuid
import httpx

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_EXTENSIONS = {
    ".pdf": "pdf",
    ".doc": "word",
    ".docx": "word",
    ".ppt": "ppt",
    ".pptx": "ppt",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
}

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


@router.post("/upload", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def upload_note(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate file extension
    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS.keys())}",
        )

    file_type = ALLOWED_EXTENSIONS[ext]

    # Read file contents asynchronously
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 10MB",
        )

    # Generate unique filename
    file_path = f"notes/{current_user.id}/{uuid.uuid4()}{ext}"

    # Upload to Supabase Storage asynchronously via httpx
    async with httpx.AsyncClient() as client:
        upload_url = f"{SUPABASE_URL}/storage/v1/object/Notes/{file_path}"
        resp = await client.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": file.content_type,
                "x-upsert": "false",
            },
            content=contents,
        )
        if resp.status_code not in (200, 201):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file",
            )

    # Create Note record
    new_note = Note(
        student_id=current_user.id,
        title=title,
        description=description,
        file_url=file_path,
        file_type=file_type,
    )

    try:
        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save note metadata",
        )

    return new_note


@router.get("/", response_model=List[NoteResponse])
async def get_notes(
    current_user: Student = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Note)
        .filter(Note.student_id == current_user.id)
        .order_by(Note.created_at.desc())
    )
    notes = result.scalars().all()

    # Generate signed URLs concurrently for all notes
    response_notes = []
    async with httpx.AsyncClient() as client:
        for note in notes:
            try:
                sign_url = f"{SUPABASE_URL}/storage/v1/object/sign/Notes/{note.file_url}"
                resp = await client.post(
                    sign_url,
                    headers={"Authorization": f"Bearer {SUPABASE_KEY}"},
                    json={"expiresIn": 3600},
                )
                if resp.status_code == 200:
                    url = f"{SUPABASE_URL}/storage/v1{resp.json()['signedURL']}"
                else:
                    url = note.file_url
            except Exception:
                url = note.file_url

            response_notes.append(
                NoteResponse(
                    id=note.id,
                    title=note.title,
                    description=note.description,
                    file_url=url,
                    file_type=note.file_type,
                    created_at=note.created_at,
                )
            )

    return response_notes
