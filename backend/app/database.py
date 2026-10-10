from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Create engine to connect to PostgreSQL
engine = create_engine(
    settings.DATABASE_URL
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Dependency to yield database sessions to routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
