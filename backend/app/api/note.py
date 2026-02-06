from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import Student
from app.models.note import Note
from app.schema.note import NoteResponse
from app.core.supabase import supabase
import os
import uuid

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
    ".png": "image"
}

@router.post("/upload", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def upload_note(
    title: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file extension
    _, ext = os.path.splitext(file.filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS.keys())}")
    
    file_type = ALLOWED_EXTENSIONS[ext]

    # Validate file size
    contents = file.file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 10MB"
        )
    file.file.seek(0)

    # Generate unique filename
    file_path = f"notes/{current_user.id}/{uuid.uuid4()}{ext}"

    # Upload to Supabase
    try:
        supabase.storage.from_("Notes").upload(
            file_path,
            contents,
            {
                "content-type": file.content_type,
                "upsert": "false"
            })
        
        stored_path = file_path

    except Exception as e:
        print(f"Supabase Upload Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file"
        )

    # Create Note record
    new_note = Note(
        student_id=current_user.id,
        title=title,
        description=description,
        file_url=stored_path,
        file_type=file_type)

    try:
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
    except Exception as e:
        db.rollback()
        # Clean up uploaded file if DB fails? -> ideally yes but keeping simple for now
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save note metadata"
        )

    return new_note

@router.get("/", response_model=List[NoteResponse])
def get_notes(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notes = db.query(Note).filter(Note.student_id == current_user.id).order_by(Note.created_at.desc()).all()
    
    # Generate signed URLs for private bucket access if needed
    # For now returning the stored object structure. 
    # If the bucket is private, we should generate signed URLs here.
    
    response_notes = []
    for note in notes:
        # Generate signed URL on the fly
        try:
            signed = supabase.storage.from_("Notes").create_signed_url(note.file_url, 3600) # 1 hour expiry
            url = signed["signedURL"]
        except:
             # Fallback or log error, keep original path if generation fails
             url = note.file_url

        response_notes.append(
            NoteResponse(
                id=note.id,
                title=note.title,
                description=note.description,
                file_url=url,
                file_type=note.file_type,
                created_at=note.created_at
            )
        )

    return response_notes
