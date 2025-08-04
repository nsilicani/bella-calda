from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from app.config import settings

DATABASE_URL = "postgresql://{db_username}:{db_passwd}@{db_host}:{db_port}/{db_name}"
engine = create_engine(
    DATABASE_URL.format(
        db_username=settings.DB_USERNAME,
        db_passwd=settings.DB_PASSWORD,
        db_host=settings.DB_HOST,
        db_port=settings.DB_PORT,
        db_name=settings.DB_NAME,
    )
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class DatabaseManager:
    """
    Handles database connection with context management
    """

    def __init__(self):
        self.db: Session = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


def create_new_db_session():
    with DatabaseManager() as db:
        yield db


def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
