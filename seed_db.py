# seed_db.py
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from werkzeug.security import generate_password_hash

from models import (
    Base,
    Student, Attendance, PointsMovement,
    Event, EventRegistration, Excuse,
    Teacher, Supervisor
)

DATABASE_URL = "sqlite:///advantage.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
)


def reset_db(db):
    # ترتيب الحذف مهم بسبب العلاقات
    db.query(EventRegistration).delete()
    db.query(PointsMovement).delete()
    db.query(Attendance).delete()
    db.query(Excuse).delete()
    db.query(Event).delete()
    db.query(Student).delete()
    db.query(Teacher).delete()
    db.query(Supervisor).delete()
    db.commit()


def add_students(db):
    # 3 طلاب لكل صف (أسماء أولى فقط)
    students_data = [
        # أول ثانوي
        dict(username="20250001", full_name="محمد", gender="male", grade="أول ثانوي", room="A1"),
        dict(username="20250002", full_name="سارة", gender="female", grade="أول ثانوي", room="A1"),
        dict(username="20250003", full_name="خالد", gender="male", grade="أول ثانوي", room="A2"),

        # ثاني ثانوي
        dict(username="20250004", full_name="نورة", gender="female", grade="ثاني ثانوي", room="B1"),
        dict(username="20250005", full_name="عبدالله", gender="male", grade="ثاني ثانوي", room="B1"),
        dict(username="20250006", full_name="ريم", gender="female", grade="ثاني ثانوي", room="B2"),

        # ثالث ثانوي
        dict(username="20250007", full_name="فيصل", gender="male", grade="ثالث ثانوي", room="C1"),
        dict(username="20250008", full_name="هيا", gender="female", grade="ثالث ثانوي", room="C1"),
        dict(username="20250009", full_name="مازن", gender="male", grade="ثالث ثانوي", room="C2"),
    ]

    students = []
    for i, s in enumerate(students_data, start=1):
        st = Student(
            username=s["username"],
            full_name=s["full_name"],
            password="1234",  # كلمة مرور الطلاب
            grade=s["grade"],
            room=s["room"],
            email=f"{s['username']}@student.com",
            phone=f"05{10000000+i}",
            national_id=s["username"],
            gender=s["gender"],
            # درجات بسيطة (قبل/بعد)
            math_pre=55 + (i % 10),
            eng_pre=50 + (i % 12),
            math_post=70 + (i % 15),
            eng_post=68 + (i % 14),
        )
        db.add(st)
        students.append(st)

    db.commit()
    return students


def add_teachers(db):
    teachers = [
        Teacher(full_name="أحمد", email="ahmad.teacher@academy.sa", subject="Math", branch="الظهران"),
        Teacher(full_name="منى", email="mona.teacher@academy.sa", subject="English", branch="الظهران"),
        Teacher(full_name="سلمان", email="salman.teacher@academy.sa", subject="Math", branch="الأحساء"),
        Teacher(full_name="لينا", email="lina.teacher@academy.sa", subject="English", branch="الأحساء"),
        Teacher(full_name="يوسف", email="yousef.teacher@academy.sa", subject="Math", branch="الرياض"),
        Teacher(full_name="هند", email="hend.teacher@academy.sa", subject="English", branch="الرياض"),
    ]
    db.add_all(teachers)
    db.commit()


def add_supervisor(db):
    # ✅ مشرف بإيميل أرامكو + رقم موظف + باسورد مشفّر
    sup = Supervisor(
        email="maan.alamer@aramco.com",
        employee_id="900123",
        full_name="مشرف",
        password_hash=generate_password_hash("Aramco@123"),
        is_active=True,
        role="coordinator",
    )
    db.add(sup)
    db.commit()


def add_attendance(db, students):
    # 10 أيام حضور/غياب لكل طالب
    start = date.today() - timedelta(days=14)
    subjects = ["Math", "English"]
    for idx, st in enumerate(students, start=1):
        absent_days = 0
        for d in range(10):
            day = start + timedelta(days=d)
            # نسوي غياب منطقي: كل طالب يغيب يوم/يومين حسب رقمه
            is_absent = (d in {3, 7} and idx % 2 == 0) or (d == 5 and idx % 3 == 0)
            if is_absent:
                absent_days += 1

            for subj in subjects:
                rec = Attendance(
                    student_id=st.id,
                    date=day,
                    subject=subj,
                    period="1",
                    status="absent" if is_absent else "present",
                    with_excuse=False,
                )
                db.add(rec)

        # نسب تقريبية
        st.absence_days = absent_days
        st.attendance_percent = int(round((10 - absent_days) / 10 * 100))
    db.commit()


def add_points(db, students):
    # حركات نقاط متنوعة لكل طالب
    reasons = [
        ("حضور ممتاز", 5),
        ("مشاركة في الحصة", 3),
        ("حل واجب", 4),
        ("تأخر", -2),
        ("عدم إحضار الدفتر", -3),
        ("مساعدة زميل", 2),
    ]

    for idx, st in enumerate(students, start=1):
        total = 0
        # 6 حركات لكل طالب
        for i in range(6):
            day = date.today() - timedelta(days=(12 - i))
            reason, change = reasons[(idx + i) % len(reasons)]
            total += change
            db.add(
                PointsMovement(
                    student_id=st.id,
                    date=day,
                    reason=reason,
                    change=change,
                    total_after=total,
                )
            )
        st.points_total = total
    db.commit()


def add_excuses(db, students):
    # أعذار: بعضها مقبول/مرفوض/قيد المراجعة
    # (بدون مرفقات حالياً)
    sample = [
        ("موعد طبي", "approved"),
        ("ظرف عائلي", "rejected"),
        ("مراجعة مستشفى", "new"),
    ]
    for idx, st in enumerate(students, start=1):
        # طالبين فقط يرفعون أعذار
        if idx % 2 == 0:
            reason, status = sample[idx % 3]
            ex = Excuse(
                student_id=st.id,
                date=date.today() - timedelta(days=6),
                reason=reason,
                status=status,
                attachment_path=None
            )
            db.add(ex)

            # نخلي الحضور في نفس اليوم "مع عذر" إذا كان مقبول
            if status == "approved":
                db.query(Attendance).filter(
                    Attendance.student_id == st.id,
                    Attendance.date == ex.date,
                    Attendance.status == "absent",
                ).update({"with_excuse": True})
    db.commit()


def add_events(db, students):
    e1 = Event(
        title="ورشة مهارات الدراسة",
        description="ورشة تفاعلية عن تنظيم الوقت والمذاكرة الفعّالة.",
        location="قاعة الأكاديمية",
        date=date.today() + timedelta(days=5),
    )
    e2 = Event(
        title="زيارة إثراء",
        description="زيارة تعليمية لتعزيز التجربة المعرفية والتعلم.",
        location="مركز إثراء",
        date=date.today() + timedelta(days=12),
    )
    e3 = Event(
        title="اختبار تجريبي (رياضيات)",
        description="اختبار قصير لقياس مستوى الطلاب.",
        location="قاعة الاختبارات",
        date=date.today() - timedelta(days=10),
    )
    db.add_all([e1, e2, e3])
    db.commit()

    # تسجيل بعض الطلاب في الفعاليات القادمة
    upcoming = [e1, e2]
    for idx, st in enumerate(students, start=1):
        if idx % 2 == 1:
            for ev in upcoming:
                db.add(EventRegistration(student_id=st.id, event_id=ev.id))
    db.commit()


def main():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        reset_db(db)

        add_teachers(db)
        add_supervisor(db)

        students = add_students(db)
        add_attendance(db, students)
        add_points(db, students)
        add_excuses(db, students)
        add_events(db, students)

        print("✅ Seed completed successfully.")
        print("Supervisor login:")
        print("  email: maan.alamer@aramco.com")
        print("  password: Aramco@123")
        print("Student login example:")
        print("  username: 20250001")
        print("  password: 1234")

    finally:
        db.close()


if __name__ == "__main__":
    main()
