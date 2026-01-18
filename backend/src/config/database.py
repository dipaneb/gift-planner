from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings
# IMPORTANT: force ORM model registration
import src.infrastructure.database.models  # noqa

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
