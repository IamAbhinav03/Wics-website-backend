"""
Initializing Database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# env for testing
# load_dotenv(".env.development.local")
# DATABASE_URL = os.environ["TEST_DATABASE_URL"]

# env for production
load_dotenv(".env")
DATABASE_URL = os.environ["POSTGRES_URL"]


# connect_args only required for sqlite
# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
