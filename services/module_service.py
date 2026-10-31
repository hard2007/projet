from database import get_connection


def list_modules():
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT m.module_id, m.module_name, m.coefficient, m.teacher_id,
                      u.full_name AS teacher_name
               FROM modules m JOIN users u ON u.user_id = m.teacher_id
               ORDER BY m.module_name"""
        ).fetchall()
    return [dict(row) for row in rows]


def add_module(module_name, coefficient, teacher_id):
    name = module_name.strip()
    coefficient = float(coefficient)
    if not name:
        raise ValueError("Module name is required.")
    if coefficient <= 0:
        raise ValueError("Coefficient must be greater than zero.")
    with get_connection() as conn:
        teacher = conn.execute(
            "SELECT role FROM users WHERE user_id = ?", (teacher_id,)
        ).fetchone()
        if teacher is None or teacher["role"] != "teacher":
            raise ValueError("Choose a valid teacher account.")
        cur = conn.execute(
            "INSERT INTO modules (module_name, coefficient, teacher_id) VALUES (?, ?, ?)",
            (name, coefficient, teacher_id),
        )
        return cur.lastrowid


def list_teachers():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT user_id, full_name FROM users WHERE role='teacher' ORDER BY full_name"
        ).fetchall()
    return [dict(row) for row in rows]


def list_students():
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT user_id, username, full_name, email, group_name
               FROM users WHERE role='student' 
               ORDER BY group_name, full_name"""
        ).fetchall()
    return [dict(row) for row in rows]


def update_student_group(student_id, group_name):
    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE users SET group_name = ? WHERE user_id = ? AND role = 'student'",
            (group_name.strip() or None, student_id),
        )
        if cur.rowcount == 0:
            raise ValueError("Student was not found.")
