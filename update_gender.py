from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Student

DATABASE_URL = "sqlite:///advantage.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

# عدّل الـ usernames هنا حسب طلابك الموجودين فعلياً في قاعدة البيانات
GENDER_BY_USERNAME = {
    "20250001": "male",
    "20250002": "female",
    "20250003": "male",
}

db = Session()
try:
    for username, gender in GENDER_BY_USERNAME.items():
        s = db.query(Student).filter(Student.username == username).first()
        if not s:
            print(f"NOT FOUND: {username}")
            continue
        s.gender = gender
        print(f"UPDATED: {username} -> {gender}")

    db.commit()
    print("DONE ✅")
finally:
    db.close()
