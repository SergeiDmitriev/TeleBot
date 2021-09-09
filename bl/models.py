from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship

engine = create_engine(
    "sqlite+pysqlite:///user.db",
    echo=True,
    future=True
)

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

Base = declarative_base()


class User_todo(Base):
    __tablename__ = "user_todo"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    text = Column(String(255), nullable=False)
    date_todo = Column(DateTime, nullable=False)

    def __str__(self):
        return self.text

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    firstname = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    phone_number = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)

    def __str__(self):
        return f""

def create_bases():
    Base.metadata.create_all(engine)