from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.api.roadmap import router as roadmap_router
from app.api.note import router as note_router
from app.api.task import router as task_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(roadmap_router)
app.include_router(note_router, prefix="/api/notes", tags=["notes"])
app.include_router(task_router, prefix="/api/tasks", tags=["tasks"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173" , "http://127.0.0.1:5173",],  # Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


