from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Base = declarative_base()


def get_engine(db_url: str = None):
    if db_url is None:
        db_path = os.path.join("data", "app.db")
        db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url, echo=False, future=True)
    return engine


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    student_code = Column(String(50), unique=True, nullable=False)
    # New identity & names
    name_ar = Column(String(120), nullable=True)
    name_en = Column(String(120), nullable=True)
    national_id = Column(String(20), nullable=True)
    # Keep a generic name for backward compatibility (optional mirror of name_en)
    name = Column(String(120), nullable=False)
    # Profile
    grade = Column(String(20), nullable=False)
    gender = Column(String(10), nullable=True)
    phone_student = Column(String(30), nullable=True)
    phone_guardian = Column(String(30), nullable=True)
    # Scores (cached per student)
    math_pre = Column(Integer, nullable=True)
    math_post = Column(Integer, nullable=True)
    eng_pre = Column(Integer, nullable=True)
    eng_post = Column(Integer, nullable=True)
    # Attendance & points (cached)
    attendance_percent = Column(Float, nullable=True)
    absence_days = Column(Integer, nullable=True)
    points_total = Column(Float, nullable=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    role = Column(String(50), nullable=True)


def create_all(db_url: str = None):
    engine = get_engine(db_url)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_all()
