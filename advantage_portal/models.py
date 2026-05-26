# models.py
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True, nullable=False)  # رقم الطالب/الهوية
    full_name = Column(String, nullable=False)  # اسم أول فقط (محمد/سارة...)
    password = Column(String, nullable=False)

    grade = Column(String, index=True, nullable=True)
    room = Column(String, nullable=True)

    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    national_id = Column(String, unique=True, nullable=True)
    gender = Column(String, nullable=True)

    math_pre = Column(Integer, nullable=True)
    eng_pre = Column(Integer, nullable=True)
    math_post = Column(Integer, nullable=True)
    eng_post = Column(Integer, nullable=True)

    attendance_percent = Column(Integer, nullable=True)
    absence_days = Column(Integer, nullable=True)

    points_total = Column(Integer, nullable=True)

    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    points = relationship("PointsMovement", back_populates="student", cascade="all, delete-orphan")
    registrations = relationship("EventRegistration", back_populates="student", cascade="all, delete-orphan")
    excuses = relationship("Excuse", back_populates="student", cascade="all, delete-orphan")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    date = Column(Date, nullable=False)
    subject = Column(String, nullable=False)
    period = Column(String, nullable=True)
    status = Column(String, nullable=False)  # present / absent
    with_excuse = Column(Boolean, default=False)

    student = relationship("Student", back_populates="attendances")


class PointsMovement(Base):
    __tablename__ = "points_movements"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    date = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
    change = Column(Integer, nullable=False)
    total_after = Column(Integer, nullable=True)

    student = relationship("Student", back_populates="points")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=True)
    date = Column(Date, nullable=False)

    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")


class EventRegistration(Base):
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)

    student = relationship("Student", back_populates="registrations")
    event = relationship("Event", back_populates="registrations")


class Excuse(Base):
    __tablename__ = "excuses"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    date = Column(Date, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(String, default="new")  # new / approved / rejected
    attachment_path = Column(String, nullable=True)

    student = relationship("Student", back_populates="excuses")


# ===================== NEW: Teachers =====================
class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)        # اسم أول فقط
    email = Column(String, unique=True, nullable=True)
    subject = Column(String, nullable=True)           # English / Math
    branch = Column(String, nullable=True)            # مثل: الظهران / الأحساء
    is_active = Column(Boolean, default=True)


# ===================== NEW: Supervisor (Aramco Email) =====================
class Supervisor(Base):
    __tablename__ = "supervisors"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)      # must be @aramco.com
    employee_id = Column(String, unique=True, nullable=True)             # رقم المشرف (اختياري)
    full_name = Column(String, nullable=True)

    password_hash = Column(String, nullable=False)  # hashed password
    is_active = Column(Boolean, default=True)
    role = Column(String, default="coordinator")    # coordinator
