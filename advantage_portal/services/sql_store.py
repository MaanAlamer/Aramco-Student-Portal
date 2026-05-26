from sqlalchemy.orm import sessionmaker
from services.sql_schema import get_engine, Student, create_all
from sqlalchemy.exc import SQLAlchemyError


class SqlStore:
    def __init__(self, db_url: str = None):
        self.engine = get_engine(db_url)
        create_all(db_url)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)

    def students_all(self):
        with self.Session() as s:
            rows = s.query(Student).all()
            out = []
            for r in rows:
                out.append({
                    "id": r.id,
                    "student_code": r.student_code,
                    "name_ar": r.name_ar,
                    "name_en": r.name_en,
                    "national_id": r.national_id,
                    "name": r.name,
                    "grade": r.grade,
                    "gender": r.gender,
                    "phone_student": r.phone_student,
                    "phone_guardian": r.phone_guardian,
                    "math_pre": r.math_pre,
                    "math_post": r.math_post,
                    "eng_pre": r.eng_pre,
                    "eng_post": r.eng_post,
                    "attendance_percent": r.attendance_percent,
                    "absence_days": r.absence_days,
                    "points_total": r.points_total
                })
            return out

    def students_save(self, students):
        with self.Session() as s:
            s.query(Student).delete()
            for st in students:
                s.add(Student(
                    student_code=st["student_code"],
                    name_ar=st.get("name_ar"),
                    name_en=st.get("name_en"),
                    national_id=st.get("national_id"),
                    name=st.get("name") or st.get("name_en") or st.get("name_ar") or "",
                    grade=st.get("grade", ""),
                    gender=st.get("gender"),
                    phone_student=st.get("phone_student"),
                    phone_guardian=st.get("phone_guardian"),
                    math_pre=st.get("math_pre"),
                    math_post=st.get("math_post"),
                    eng_pre=st.get("eng_pre"),
                    eng_post=st.get("eng_post"),
                    attendance_percent=st.get("attendance_percent"),
                    absence_days=st.get("absence_days"),
                    points_total=st.get("points_total")
                ))
            s.commit()

    def users_save(self, users):
        # simple users save using low-level INSERT/REPLACE for demo
        from sqlalchemy import text
        with self.engine.connect() as conn:
            for u in users:
                try:
                    conn.execute(text("INSERT OR REPLACE INTO users (username,password,role) VALUES (:u,:p,:r)"),
                                 {"u": u.get("username"), "p": u.get("password"), "r": u.get("role")})
                except Exception:
                    pass
