"""
Initializing Database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# sqlite db for testing
# DATABASE_URL = "sqlite:///./wics.db"
DATABASE_URL = "postgresql://default:jSJg6x8vfXuL@ep-round-mouse-a1oo2jy0-pooler.ap-southeast-1.aws.neon.tech:5432/verceldb?sslmode=require"

# connect_args only required for sqlite
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
