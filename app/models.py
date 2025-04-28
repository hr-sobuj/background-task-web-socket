from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False)
    result = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
