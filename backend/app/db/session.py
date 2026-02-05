from sqlalchemy import create_engine # type: ignore
from sqlalchemy.orm import sessionmaker # type: ignore
from ..core.config import settings

engine  = create_engine(settings.DATABASE_URL , future =True, connect_args={"sslmode": "require"}, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit = False , autoflush = False , bind = engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()