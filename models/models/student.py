from sqlalchemy import Column, Integer, String
from app import db

class Student(db.Model):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    grade = Column(String(50), nullable=True)
    room = Column(String(50), nullable=True)

    def __repr__(self):
        return f"<Student {self.username}>"
