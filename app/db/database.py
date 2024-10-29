import os
from typing import Generator, Any

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Base = declarative_base()
session = sessionmaker(bind=engine)

def get_db() -> Generator[Session, Any, None]:
    db = session()
    try:
        yield db
    finally:
        db.close()
