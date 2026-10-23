"""Run once to create demo accounts and sample modules; change passwords before use."""
from database import initialize_database, get_connection
from services.auth_service import create_user
from services.module_service import add_module

initialize_database()


def get_id(username):
    with get_connection() as conn:
        row = conn.execute("SELECT user_id FROM users WHERE username=?", (username,)).fetchone()
    return row["user_id"] if row else None


def ensure_user(username, password, role, full_name, email=None, group_name=None):
    existing = get_id(username)
    if existing:
        return existing
    return create_user(username, password, role, full_name, email, group_name)


teacher_id = ensure_user("teacher1", "TeacherDemo123!", "teacher", "Demo Teacher", "teacher@example.test")
student1_id = ensure_user("student1", "StudentDemo123!", "student", "Demo Student One", "student1@example.test", "G2")
student2_id = ensure_user("student2", "StudentDemo123!", "student", "Demo Student Two", "student2@example.test", "G2")

with get_connection() as conn:
    existing = conn.execute("SELECT module_id FROM modules WHERE module_name='Python'").fetchone()
if not existing:
    add_module("Python", 3, teacher_id)

print("Demo accounts ready.")
print("Teacher: teacher1 / TeacherDemo123!")
print("Student: student1 / StudentDemo123!")
print("Student: student2 / StudentDemo123!")
print("Change these demonstration passwords before using real data.")
