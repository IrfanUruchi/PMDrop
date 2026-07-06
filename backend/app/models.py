from sqlalchemy import Column, Integer, String, BigInteger
from app.database import Base


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    size = Column(BigInteger)
    path = Column(String)
    uploaded_at = Column(BigInteger)


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    ip = Column(String)
    last_seen = Column(BigInteger)
