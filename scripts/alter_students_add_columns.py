from sqlalchemy import text
from services.sql_schema import get_engine

cols = [
    ("name_ar","VARCHAR(120)"),
    ("name_en","VARCHAR(120)"),
    ("national_id","VARCHAR(20)"),
    ("phone_student","VARCHAR(30)"),
    ("phone_guardian","VARCHAR(30)"),
    ("math_pre","INTEGER"),
    ("math_post","INTEGER"),
    ("eng_pre","INTEGER"),
    ("eng_post","INTEGER"),
    ("attendance_percent","FLOAT"),
    ("absence_days","INTEGER"),
    ("points_total","FLOAT")
]

engine = get_engine()
with engine.connect() as conn:
    for name, typ in cols:
        try:
            conn.execute(text(f"ALTER TABLE students ADD COLUMN {name} {typ}"))
        except Exception:
            pass
    conn.commit()
print("Altered students table (if needed).")
