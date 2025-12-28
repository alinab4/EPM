from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Check if we should use SQLite (for quick testing) or PostgreSQL
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"

if USE_SQLITE:
    # SQLite for quick testing/development
    DB_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "employee.db")
    DB_URL = f"sqlite:///{DB_FILE}"
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
else:
    # PostgreSQL Configuration
    DB_URL = os.getenv("DATABASE_URL")
    if DB_URL and DB_URL.startswith("postgres://"):
        DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)
        
    if not DB_URL:
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "epm_db")
        DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Create engine
    engine = create_engine(DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """
    Initializes the database by creating all tables defined in the models.
    This function should be called at application startup.
    """
    from . import models
    Base.metadata.create_all(bind=engine)
