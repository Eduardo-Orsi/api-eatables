import os
from typing import Generator, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base


ENV_SETUP = os.getenv("ENV_SETUP")
DATABASE_URL = os.getenv("DATABASE_URL")

if ENV_SETUP == "PROD": 
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,             # Set initial pool size
        max_overflow=20,          # Allow for temporary overflow
        pool_timeout=30,          # Seconds to wait for connection
        pool_recycle=1800,        # Recycle connections every 30 minutes
        pool_pre_ping=True        # Check connection health before using
    )
else:
    engine = create_engine("sqlite:///./tests.db")

Base = declarative_base()
session_factory = sessionmaker(bind=engine)
session = scoped_session(session_factory)

def not_async_get_db() -> Session:
    return session()

def get_db() -> Generator[Session, Any, None]:
    db = session()
    try:
        yield db
    finally:
        db.close()
