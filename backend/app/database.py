import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_PATH = os.getenv(
    "PMDROP_DATABASE_PATH",
    "./data/pmdrop.db"
)

database_directory = os.path.dirname(DATABASE_PATH)

if database_directory:
    os.makedirs(database_directory, exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
