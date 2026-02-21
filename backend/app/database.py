from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# ── Engine + Session ──
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── Base class cho ORM models ──
Base = declarative_base()


# ── Dependency Injection ──
def get_db():
    """FastAPI dependency: mở DB session, tự đóng sau khi request xong."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
