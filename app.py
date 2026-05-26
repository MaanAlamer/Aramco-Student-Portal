from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
import os
import re
from functools import wraps
from datetime import timedelta, date, datetime
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from sqlalchemy.exc import OperationalError

from models import (
    Base,
    Student,
    Attendance,
    PointsMovement,
    Event,
    EventRegistration,
    Excuse,
)

# ✅ استيراد Supervisor بشكل آمن (عشان لو ما أضفته بعد، ما يطيح السيرفر)
try:
    from models import Supervisor
except Exception:
    Supervisor = None


app = Flask(__name__)
app.secret_key = "change_me_secret"
app.permanent_session_lifetime = timedelta(hours=6)

# ================== Folders ==================
IMAGES_DIR = os.path.join("static", "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

UPLOADS_DIR = os.path.join("static", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ✅ إعدادات رفع الملفات
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}
MAX_UPLOAD_MB = 6
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024  # 6MB

# ================== Database ==================
DATABASE_URL = "sqlite:///advantage.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# ✅ مهم جداً: expire_on_commit=False يمنع DetachedInstanceError بعد commit
SessionLocal = scoped_session(
    sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False
    )
)

Base.metadata.create_all(bind=engine)


@app.teardown_appcontext
def remove_session(exception=None):
    SessionLocal.remove()


# ================== Helpers ==================
def hero_static_filename():
    assets_path = os.path.join("static", "assets", "logoAA-removebg-preview.png")
    images_path = os.path.join("static", "images", "logoAA-removebg-preview.png")
    if os.path.exists(assets_path):
        return "assets/logoAA-removebg-preview.png"
    if os.path.exists(images_path):
        return "images/logoAA-removebg-preview.png"
    return "assets/logoAA-removebg-preview.png"


def require_student(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = session.get("user")
        if not user or user.get("role") != "student":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def require_coordinator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = session.get("user")
        if not user or user.get("role") != "coordinator":
            return redirect(url_for("coordinator_login"))
        return f(*args, **kwargs)
    return wrapper


def is_aramco_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip().lower()
    return bool(re.fullmatch(r"[a-z0-9._%+\-]+@aramco\.com", email))


def normalize_gender(value: str) -> str:
    if value is None:
        return ""
    s = str(value).strip().lower()
    male_set = {"m", "male", "ذكر", "ولد", "boy", "man", "بنين", "طلاب", "طالب"}
    female_set = {"f", "female", "أنثى", "انثى", "بنت", "girl", "woman", "بنات", "طالبات", "طالبة"}
    if s in male_set:
        return "male"
    if s in female_set:
        return "female"
    return ""


def safe_avg(nums):
    vals = [x for x in nums if x is not None]
    if not vals:
        return 0
    return round(sum(vals) / len(vals), 1)


def student_subject_score(student: Student, subject: str) -> int:
    if subject == "math":
        return int(student.math_post) if student.math_post is not None else int(student.math_pre or 0)
    if subject == "english":
        return int(student.eng_post) if student.eng_post is not None else int(student.eng_pre or 0)
    return 0


def get_current_student(db):
    user = session.get("user") or {}
    username = user.get("username")
    if not username:
        return None
    return db.query(Student).filter(Student.username == username).first()


def is_event_past(event_date):
    if not event_date:
        return False
    return event_date < date.today()


def normalize_excuse_status(status: str) -> str:
    s = (status or "").strip().lower()
    if s in ("new", "approved", "rejected"):
        return s
    return "new"


def excuse_status_ar(status: str) -> str:
    s = normalize_excuse_status(status)
    if s == "approved":
        return "مقبول"
    if s == "rejected":
        return "مرفوض"
    return "قيد المراجعة"


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None

    filename = secure_filename(file_storage.filename)
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    final_name = f"{stamp}_{filename}"
    full_path = os.path.join(UPLOADS_DIR, final_name)
    file_storage.save(full_path)
    return f"static/uploads/{final_name}"


def establish_demo_student_session():
    """عرض تجريبي: جلسة طالب من أول سجل في قاعدة البيانات."""
    db = SessionLocal()
    try:
        db_student = db.query(Student).order_by(Student.id.asc()).first()
        if not db_student:
            return False
        session["user"] = {
            "username": db_student.username,
            "full_name": db_student.full_name,
            "role": "student",
            "student_id": db_student.id,
        }
        session.permanent = True
        return True
    finally:
        db.close()


def establish_demo_coordinator_session():
    """عرض تجريبي: جلسة مشرف من قاعدة البيانات أو جلسة افتراضية."""
    if Supervisor is not None:
        db = SessionLocal()
        try:
            sup = (
                db.query(Supervisor)
                .filter(Supervisor.is_active == True)  # noqa: E712
                .order_by(Supervisor.id.asc())
                .first()
            )
            if not sup:
                sup = db.query(Supervisor).order_by(Supervisor.id.asc()).first()
            if sup:
                session["user"] = {
                    "username": sup.email,
                    "role": "coordinator",
                    "full_name": sup.full_name or "مشرف الأكاديمية",
                    "supervisor_id": sup.id,
                }
                session.permanent = True
                return True
        finally:
            db.close()

    session["user"] = {
        "username": "demo@aramco.com",
        "role": "coordinator",
        "full_name": "مشرف (عرض تجريبي)",
        "supervisor_id": None,
    }
    session.permanent = True
    return True


# ================== Routes ==================
@app.route("/")
def index():
    return redirect(url_for("login"))


# ================== Auth (طلاب فقط) ==================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        enter = request.args.get("enter")
        if enter == "student":
            if establish_demo_student_session():
                return redirect(url_for("student_dashboard"))
            return render_template(
                "login.html",
                error="لا يوجد طلاب في قاعدة البيانات. شغّل seed_db.py أولاً.",
                hero_filename=hero_static_filename(),
            )
        if enter == "coordinator":
            establish_demo_coordinator_session()
            return redirect(url_for("coordinator_dashboard"))
        return render_template("login.html", hero_filename=hero_static_filename())

    entered = (request.form.get("username", "").strip()
               or request.form.get("identity", "").strip())
    password = request.form.get("password", "").strip()
    login_type = request.form.get("mode", "login")

    if login_type == "register":
        return redirect(url_for("register_student"))

    # ✅ نمنع فقط إيميل أرامكو (مشرف) — لا نمنع الأرقام لأن أرقام الطلاب كلها digits
    if is_aramco_email(entered):
        return render_template(
            "login.html",
            error="تسجيل دخول المشرف له صفحة خاصة. اضغط (تسجيل دخول مشرف).",
            hero_filename=hero_static_filename()
        )

    db = SessionLocal()
    try:
        db_student = (
            db.query(Student)
            .filter(
                Student.username == entered,
                Student.password == password
            )
            .first()
        )
    finally:
        db.close()

    if db_student:
        session["user"] = {
            "username": db_student.username,
            "full_name": db_student.full_name,
            "role": "student",
            "student_id": db_student.id,
        }
        session.permanent = True
        return redirect(url_for("student_dashboard"))

    return render_template(
        "login.html",
        error="بيانات غير صحيحة",
        hero_filename=hero_static_filename()
    )


# ================== Coordinator Login (مشرف) ==================
@app.route("/coordinator/login", methods=["GET", "POST"])
def coordinator_login():
    # لو داخل بالفعل كمشرف
    if (session.get("user") or {}).get("role") == "coordinator":
        return redirect(url_for("coordinator_dashboard"))

    if Supervisor is None:
        return render_template(
            "coordinator_login.html",
            error="جدول المشرفين (Supervisor) غير مضاف في models.py حالياً.",
            hero_filename=hero_static_filename()
        )

    if request.method == "GET":
        return render_template("coordinator_login.html", hero_filename=hero_static_filename())

    identity = (request.form.get("identity") or "").strip()
    password = (request.form.get("password") or "").strip()

    if not identity or not password:
        return render_template(
            "coordinator_login.html",
            error="فضلاً أدخل البريد الإلكتروني (أرامكو) أو رقم الموظف + كلمة المرور.",
            hero_filename=hero_static_filename()
        )

    db = SessionLocal()
    try:
        sup = None

        if "@" in identity:
            email = identity.lower()
            if not is_aramco_email(email):
                return render_template(
                    "coordinator_login.html",
                    error="التسجيل متاح فقط لإيميلات أرامكو (@aramco.com).",
                    hero_filename=hero_static_filename()
                )
            sup = db.query(Supervisor).filter(Supervisor.email == email).first()
        else:
            sup = db.query(Supervisor).filter(Supervisor.employee_id == identity).first()

        if sup and getattr(sup, "is_active", True) and check_password_hash(sup.password_hash, password):
            session["user"] = {
                "username": sup.email,
                "role": "coordinator",
                "full_name": sup.full_name or "مشرف الأكاديمية",
                "supervisor_id": sup.id,
            }
            session.permanent = True
            return redirect(url_for("coordinator_dashboard"))
    finally:
        db.close()

    return render_template(
        "coordinator_login.html",
        error="بيانات المشرف غير صحيحة.",
        hero_filename=hero_static_filename()
    )


# ✅ Alias/توافق: لو فيه أي مكان يفتح /coordinator/register لا يطيح
@app.route("/coordinator/register", methods=["GET", "POST"])
def coordinator_register():
    return redirect(url_for("coordinator_login"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ================== Coordinator Dashboard ==================
@app.route("/coordinator/dashboard")
@require_coordinator
def coordinator_dashboard():
    user = session.get("user")

    db = SessionLocal()
    try:
        students = db.query(Student).order_by(Student.id.asc()).all()
        total_students = len(students)

        for s in students:
            total = (
                db.query(func.coalesce(func.sum(PointsMovement.change), 0))
                .filter(PointsMovement.student_id == s.id)
                .scalar()
            )
            s.points_total = int(total or 0)

        males = 0
        females = 0
        for s in students:
            g = normalize_gender(getattr(s, "gender", None))
            if g == "male":
                males += 1
            elif g == "female":
                females += 1
        if (males + females) < total_students:
            females = total_students - males

        pre_vals = []
        post_vals = []
        for s in students:
            if s.math_pre is not None:
                pre_vals.append(s.math_pre)
            if s.eng_pre is not None:
                pre_vals.append(s.eng_pre)
            if s.math_post is not None:
                post_vals.append(s.math_post)
            if s.eng_post is not None:
                post_vals.append(s.eng_post)

        pre_avg = safe_avg(pre_vals)
        post_avg = safe_avg(post_vals)

        phases = ["أول ثانوي", "ثاني ثانوي", "ثالث ثانوي"]
        top_students = {}
        for phase in phases:
            phase_students = [st for st in students if (st.grade or "") == phase]
            top_math = sorted(phase_students, key=lambda st: student_subject_score(st, "math"), reverse=True)[:3]
            top_english = sorted(phase_students, key=lambda st: student_subject_score(st, "english"), reverse=True)[:3]
            top_students[phase] = {"math": top_math, "english": top_english}

        excuses = (
            db.query(Excuse)
            .options(joinedload(Excuse.student))
            .order_by(Excuse.date.desc())
            .limit(50)
            .all()
        )
    finally:
        db.close()

    return render_template(
        "coordinator_dashboard.html",
        user=user,
        students=students,
        total_students=total_students,
        males=males,
        females=females,
        pre_avg=pre_avg,
        post_avg=post_avg,
        top_students=top_students,
        excuses=excuses,
    )


# ================== Coordinator Excuses ==================
@app.route("/coordinator/excuses")
@require_coordinator
def coordinator_excuses():
    grade = (request.args.get("grade") or "all").strip()
    status = normalize_excuse_status(request.args.get("status") or "new")
    q = (request.args.get("q") or "").strip()

    limit = request.args.get("limit") or "50"
    try:
        limit_n = int(limit)
    except ValueError:
        limit_n = 50
    limit_n = max(10, min(limit_n, 200))

    db = SessionLocal()
    try:
        query = (
            db.query(Excuse)
            .options(joinedload(Excuse.student))
            .order_by(Excuse.date.desc(), Excuse.id.desc())
        )

        if status:
            query = query.filter(Excuse.status == status)

        if grade and grade != "all":
            query = query.join(Student, Student.id == Excuse.student_id).filter(Student.grade == grade)

        if q:
            query = query.join(Student, Student.id == Excuse.student_id).filter(
                (Student.full_name.contains(q)) | (Student.username.contains(q))
            )

        rows = query.limit(limit_n).all()

        data = []
        for ex in rows:
            st = ex.student
            data.append({
                "id": ex.id,
                "student_name": (st.full_name if st else "—"),
                "student_username": (st.username if st else "—"),
                "grade": (st.grade if st and st.grade else "غير محدد"),
                "date": ex.date.strftime("%Y-%m-%d") if ex.date else "",
                "reason": ex.reason or "",
                "status": normalize_excuse_status(ex.status),
                "status_ar": excuse_status_ar(ex.status),
                "attachment_path": ex.attachment_path or "",
                "attachment_url": (url_for("static", filename=ex.attachment_path.replace("static/", "", 1))
                                   if ex.attachment_path and ex.attachment_path.startswith("static/")
                                   else ("/" + ex.attachment_path if ex.attachment_path else "")),
            })

        grades_list = ["أول ثانوي", "ثاني ثانوي", "ثالث ثانوي"]
    finally:
        db.close()

    return render_template(
        "coordinator_excuses.html",
        rows=data,
        grade=grade,
        status=status,
        q=q,
        limit=limit_n,
        grades_list=grades_list,
    )


@app.route("/coordinator/excuses/<int:excuse_id>/approve", methods=["POST"])
@require_coordinator
def approve_excuse(excuse_id):
    db = SessionLocal()
    try:
        ex = db.query(Excuse).filter(Excuse.id == excuse_id).first()
        if not ex:
            flash("العذر غير موجود.")
            return redirect(url_for("coordinator_excuses"))
        ex.status = "approved"
        db.commit()
        flash("تم قبول العذر ✅")
    finally:
        db.close()
    return redirect(url_for("coordinator_excuses", status="new"))


@app.route("/coordinator/excuses/<int:excuse_id>/reject", methods=["POST"])
@require_coordinator
def reject_excuse(excuse_id):
    db = SessionLocal()
    try:
        ex = db.query(Excuse).filter(Excuse.id == excuse_id).first()
        if not ex:
            flash("العذر غير موجود.")
            return redirect(url_for("coordinator_excuses"))
        ex.status = "rejected"
        db.commit()
        flash("تم رفض العذر ❌")
    finally:
        db.close()
    return redirect(url_for("coordinator_excuses", status="new"))


# ================== Student Pages ==================
@app.route("/student/dashboard")
@require_student
def student_dashboard():
    user = session.get("user")
    student_name = user.get("full_name") or user.get("username", "الطالب")
    return render_template("student_dashboard.html", student_name=student_name)


@app.route("/student/schedule")
@require_student
def student_schedule():
    db = SessionLocal()
    try:
        user = session.get("user") or {}
        student_name = user.get("full_name") or user.get("username", "الطالب")
        student_id = user.get("student_id")

        s = get_current_student(db)
        grade = (s.grade if s and getattr(s, "grade", None) else "غير محدد")
        room = (getattr(s, "room", None) if s else None) or "غير محدد"

        return render_template(
            "student_schedule.html",
            student_name=student_name,
            grade=grade,
            room=room,
            debug_username=user.get("username", ""),
            debug_id=student_id or "",
        )
    finally:
        db.close()


@app.route("/student/register", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        nid = request.form.get("identity", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        pwd = request.form.get("password", "").strip()
        pwd2 = request.form.get("password2", "").strip()

        if not all([full_name, nid, email, pwd, pwd2]):
            return render_template("register_student.html", error="جميع الحقول مطلوبة")

        if pwd != pwd2:
            return render_template("register_student.html", error="كلمتا المرور غير متطابقتين")

        db = SessionLocal()
        try:
            existing = db.query(Student).filter(Student.username == nid).first()
            if existing:
                return render_template("register_student.html", error="رقم الهوية مسجل مسبقاً")

            new_student = Student(
                username=nid,
                full_name=full_name,
                password=pwd,
                grade="غير محدد",
                email=email,
                phone=phone,
                national_id=nid,
            )
            db.add(new_student)
            db.commit()
        finally:
            db.close()

        return render_template("register_student.html", info="تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.")

    return render_template("register_student.html")


@app.route("/student/excuses", methods=["GET", "POST"])
@require_student
def student_excuses():
    user = session.get("user") or {}
    student_name = user.get("full_name") or user.get("username", "الطالب")
    student_id = user.get("student_id")

    if not student_id:
        flash("لم يتم تحديد الطالب في الجلسة، أعد تسجيل الدخول.")
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        if request.method == "POST":
            date_str = (request.form.get("date") or "").strip()
            reason = (request.form.get("reason") or "").strip()
            attachment = request.files.get("attachment")

            if not date_str or not reason:
                flash("فضلاً أدخل التاريخ وسبب العذر.")
                return redirect(url_for("student_excuses"))

            try:
                ex_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("صيغة التاريخ غير صحيحة.")
                return redirect(url_for("student_excuses"))

            attachment_path = None
            if attachment and attachment.filename:
                attachment_path = save_uploaded_file(attachment)
                if attachment_path is None:
                    flash("نوع الملف غير مسموح. المسموح: png, jpg, jpeg, pdf")
                    return redirect(url_for("student_excuses"))

            new_ex = Excuse(
                student_id=student_id,
                date=ex_date,
                reason=reason,
                status="new",
                attachment_path=attachment_path
            )
            db.add(new_ex)
            db.commit()
            flash("تم رفع العذر بنجاح ✅ (قيد المراجعة)")
            return redirect(url_for("student_excuses"))

        items = (
            db.query(Excuse)
            .filter(Excuse.student_id == student_id)
            .order_by(Excuse.date.desc(), Excuse.id.desc())
            .all()
        )

        rows = []
        for ex in items:
            rows.append({
                "id": ex.id,
                "date": ex.date.strftime("%Y-%m-%d") if ex.date else "",
                "reason": ex.reason or "",
                "status": normalize_excuse_status(ex.status),
                "status_ar": excuse_status_ar(ex.status),
                "attachment_path": ex.attachment_path or "",
                "attachment_url": (url_for("static", filename=ex.attachment_path.replace("static/", "", 1))
                                   if ex.attachment_path and ex.attachment_path.startswith("static/")
                                   else ("/" + ex.attachment_path if ex.attachment_path else "")),
            })
    finally:
        db.close()

    return render_template("student_excuses.html", student_name=student_name, rows=rows)


@app.route("/student/attendance")
@require_student
def student_attendance():
    db = SessionLocal()
    try:
        s = get_current_student(db)
        user = session.get("user") or {}
        student_id = user.get("student_id")

        student_name = (s.full_name if s else (user.get("full_name") or user.get("username", "الطالب")))
        student_grade = (s.grade if s and s.grade else "غير محدد")
        student_room = (getattr(s, "room", None) if s else None) or "غير محدد"

        max_absence_percentage = 25

        records = (
            db.query(Attendance)
            .filter(Attendance.student_id == student_id)
            .order_by(Attendance.date.desc())
            .all()
        ) if student_id else []

        total_sessions = len(records)
        absent_records = [r for r in records if r.status == "absent"]
        absent_sessions = len(absent_records)

        if total_sessions > 0:
            absence_percentage = round(absent_sessions / total_sessions * 100, 1)
            presence_percentage = round(100 - absence_percentage, 1)
            max_allowed_absences = round(max_absence_percentage * total_sessions / 100)
        else:
            absence_percentage = 0
            presence_percentage = 0
            max_allowed_absences = 0

        remaining_absences = max(0, max_allowed_absences - absent_sessions)

        absences = [
            {
                "date": r.date.strftime("%Y-%m-%d") if r.date else "",
                "subject": r.subject,
                "period": r.period or "",
                "with_excuse": bool(getattr(r, "with_excuse", False)),
                "note": "تم تسجيل غيابك في هذا اليوم.",
            }
            for r in absent_records
        ]

    except OperationalError:
        student_name = session.get("user", {}).get("full_name") or "الطالب"
        student_grade = "غير محدد"
        student_room = "غير محدد"
        max_absence_percentage = 25
        total_sessions = 0
        absent_sessions = 0
        presence_percentage = 0
        absence_percentage = 0
        remaining_absences = 0
        absences = []
        flash("حصل خطأ في قاعدة البيانات.")
    finally:
        db.close()

    return render_template(
        "student_attendance.html",
        student_name=student_name,
        grade=student_grade,
        room=student_room,  # ✅ تم تمرير الغرفة
        total_sessions=total_sessions,
        absent_sessions=absent_sessions,
        presence_percentage=presence_percentage,
        absence_percentage=absence_percentage,
        max_absence_percentage=max_absence_percentage,
        remaining_absences=remaining_absences,
        remaining_sessions=remaining_absences,
        absences=absences,
    )


@app.route("/student/points")
@require_student
def student_points():
    user = session.get("user") or {}
    student_name = user.get("full_name") or user.get("username", "الطالب")
    student_id = user.get("student_id")

    db = SessionLocal()
    try:
        if not student_id:
            flash("لم يتم تحديد الطالب في الجلسة، أعد تسجيل الدخول.")
            return redirect(url_for("login"))

        moves = (
            db.query(PointsMovement)
            .filter(PointsMovement.student_id == student_id)
            .order_by(PointsMovement.date.desc(), PointsMovement.id.desc())
            .all()
        )

        total_points = (
            db.query(func.coalesce(func.sum(PointsMovement.change), 0))
            .filter(PointsMovement.student_id == student_id)
            .scalar()
        )

        max_points = 100
        percentage = round((total_points / max_points) * 100, 1) if max_points > 0 else 0

        if total_points >= 80:
            level = "طالب متميّز"
        elif total_points >= 50:
            level = "طالب نشيط"
        elif total_points > 0:
            level = "طالب يحتاج لتحسين"
        else:
            level = "لا توجد نقاط بعد"

        return render_template(
            "student_points.html",
            student_name=student_name,
            total_points=total_points,
            max_points=max_points,
            percentage=percentage,
            level=level,
            moves=moves,
        )
    finally:
        db.close()


@app.route("/student/events")
@require_student
def student_events():
    user = session.get("user") or {}
    student_name = user.get("full_name") or user.get("username", "الطالب")
    student_id = user.get("student_id")

    tab = (request.args.get("tab") or "upcoming").strip().lower()
    today = date.today()

    db = SessionLocal()
    try:
        reg_counts = dict(
            db.query(EventRegistration.event_id, func.count(EventRegistration.id))
            .group_by(EventRegistration.event_id)
            .all()
        )

        events = db.query(Event).order_by(Event.date.asc()).all()

        regs = (
            db.query(EventRegistration)
            .filter(EventRegistration.student_id == student_id)
            .all()
        ) if student_id else []
        registered_ids = {r.event_id for r in regs}

        events_data = []
        for e in events:
            past = is_event_past(e.date)
            events_data.append(
                {
                    "id": e.id,
                    "title": e.title,
                    "description": e.description or "",
                    "location": e.location or "",
                    "date": e.date.strftime("%Y-%m-%d") if e.date else "",
                    "is_registered": e.id in registered_ids,
                    "is_past": past,
                    "can_register": (not past),
                    "registrations_count": int(reg_counts.get(e.id, 0)),
                }
            )

        if tab == "past":
            filtered = [x for x in events_data if x["is_past"]]
        elif tab == "all":
            filtered = events_data
        else:
            filtered = [x for x in events_data if not x["is_past"]]

    finally:
        db.close()

    return render_template(
        "student_events.html",
        student_name=student_name,
        events=filtered,
        tab=tab,
        today=today.strftime("%Y-%m-%d"),
    )


@app.route("/student/events/register/<int:event_id>", methods=["POST"])
@require_student
def register_event(event_id):
    user = session.get("user") or {}
    student_id = user.get("student_id")

    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            flash("لم يتم العثور على هذه الفعالية.")
            return redirect(url_for("student_events"))

        if is_event_past(event.date):
            flash("لا يمكن التسجيل في فعالية منتهية.")
            return redirect(url_for("student_events", tab="upcoming"))

        exists = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.student_id == student_id,
                EventRegistration.event_id == event_id,
            )
            .first()
        )

        if exists:
            flash("أنت مسجّل مسبقاً في هذه الفعالية.")
        else:
            reg = EventRegistration(student_id=student_id, event_id=event_id)
            db.add(reg)
            db.commit()
            flash("تم تسجيلك في الفعالية بنجاح ✅")
    finally:
        db.close()

    return redirect(url_for("student_events", tab="upcoming"))


@app.route("/student/events/unregister/<int:event_id>", methods=["POST"])
@require_student
def unregister_event(event_id):
    user = session.get("user") or {}
    student_id = user.get("student_id")

    db = SessionLocal()
    try:
        reg = (
            db.query(EventRegistration)
            .filter(
                EventRegistration.student_id == student_id,
                EventRegistration.event_id == event_id,
            )
            .first()
        )
        if not reg:
            flash("أنت غير مسجّل في هذه الفعالية.")
            return redirect(url_for("student_events"))

        db.delete(reg)
        db.commit()
        flash("تم إلغاء التسجيل بنجاح ✅")
    finally:
        db.close()

    return redirect(url_for("student_events", tab="upcoming"))


if __name__ == "__main__":
    app.run(debug=True)
