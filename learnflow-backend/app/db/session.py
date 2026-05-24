from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

# Convert postgres:// to postgresql+asyncpg:// for async driver
ASYNC_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
).replace(
    "postgres://", "postgresql+asyncpg://"
)

# Remove sslmode from query params for asyncpg (uses ssl=True instead)
if "sslmode=require" in ASYNC_DATABASE_URL:
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("?sslmode=require", "").replace("&sslmode=require", "")

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Keep sync engine for migrations/table creation only
SYNC_DATABASE_URL = settings.DATABASE_URL
if not SYNC_DATABASE_URL.startswith("postgresql://"):
    SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgres://", "postgresql://")

engine = create_engine(
    SYNC_DATABASE_URL,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,
)
