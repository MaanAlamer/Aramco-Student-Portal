from services.sql_store import SqlStore

def seed():
    store = SqlStore()
    if store.students_all():
        print("DB already seeded")
        return

    users = [
        {"username":"coordinator","password":"1234","role":"coordinator"},
        {"username":"s1001","password":"0000","role":"student"},
        {"username":"s1002","password":"1111","role":"student"}
    ]
    store.users_save(users)

    students = [
        {
            "student_code":"s1001",
            "name_ar":"علي أحمد",
            "name_en":"Ali Ahmed",
            "national_id":"1012345678",
            "name":"Ali Ahmed",
            "grade":"10",
            "gender":"Male",
            "phone_student":"0501111111",
            "phone_guardian":"0552222222",
            "math_pre":60, "math_post":82,
            "eng_pre":58,  "eng_post":76,
            "attendance_percent":90.0,
            "absence_days":3,
            "points_total":27
        },
        {
            "student_code":"s1002",
            "name_ar":"سارة محمد",
            "name_en":"Sara Mohammed",
            "national_id":"1023456789",
            "name":"Sara Mohammed",
            "grade":"10",
            "gender":"Female",
            "phone_student":"0503333333",
            "phone_guardian":"0554444444",
            "math_pre":72, "math_post":79,
            "eng_pre":70,  "eng_post":85,
            "attendance_percent":88.0,
            "absence_days":4,
            "points_total":31
        }
    ]
    store.students_save(students)

    print("Seeded DB with demo data (students + new columns)")

if __name__ == "__main__":
    seed()
