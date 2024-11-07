import os
from typing import Generator, Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base


ENV_SETUP = os.getenv("ENV_SETUP")
DATABASE_URL = os.getenv("DATABASE_URL")

if ENV_SETUP == "PROD": 
    engine = create_engine(DATABASE_URL)
else:
    engine = create_engine("sqlite:///./tests.db")

Base = declarative_base()
session = sessionmaker(bind=engine)

def get_db() -> Generator[Session, Any, None]:
    db = session()
    try:
        yield db
    finally:
        db.close()
