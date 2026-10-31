from database import get_connection

COURSEWORK_WEIGHT = 0.40
EXAM_WEIGHT = 0.60


def _validate_mark(mark, label):
    if mark is None or str(mark).strip() == "":
        return None
    value = float(mark)
    if not 0 <= value <= 20:
        raise ValueError(f"{label} must be between 0 and 20.")
    return value


def calculate_module_average(coursework_mark, exam_mark):
    if coursework_mark is None or exam_mark is None:
        return None
    return coursework_mark * COURSEWORK_WEIGHT + exam_mark * EXAM_WEIGHT


def upsert_grade(student_id, module_id, coursework_mark, exam_mark, teacher_id):
    coursework = _validate_mark(coursework_mark, "Coursework mark")
    exam = _validate_mark(exam_mark, "Exam mark")
    if coursework is None and exam is None:
        raise ValueError("Enter at least one mark.")

    with get_connection() as conn:
        module = conn.execute(
            "SELECT teacher_id FROM modules WHERE module_id = ?", (module_id,)
        ).fetchone()
        if module is None:
            raise ValueError("Module not found.")
        if module["teacher_id"] != teacher_id:
            raise PermissionError("You can only enter grades for your assigned modules.")

        student = conn.execute(
            "SELECT role FROM users WHERE user_id = ?", (student_id,)
        ).fetchone()
        if student is None or student["role"] != "student":
            raise ValueError("Choose a valid student account.")

        conn.execute(
            """INSERT INTO grades (student_id, module_id, coursework_mark, exam_mark)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(student_id, module_id) DO UPDATE SET
                 coursework_mark=excluded.coursework_mark,
                 exam_mark=excluded.exam_mark""",
            (student_id, module_id, coursework, exam),
        )


def get_teacher_modules(teacher_id):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT module_id, module_name, coefficient
               FROM modules WHERE teacher_id = ? ORDER BY module_name""",
            (teacher_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_students_for_module(module_id, teacher_id):
    with get_connection() as conn:
        module = conn.execute(
            "SELECT module_id FROM modules WHERE module_id=? AND teacher_id=?",
            (module_id, teacher_id),
        ).fetchone()
        if module is None:
            raise PermissionError("This module is not assigned to you.")
        
        rows = conn.execute(
            """SELECT u.user_id, u.full_name, u.username, u.group_name,
                      g.coursework_mark, g.exam_mark
               FROM users u
               LEFT JOIN grades g ON g.student_id = u.user_id AND g.module_id = ?
               WHERE u.role='student' 
               ORDER BY u.group_name, u.full_name""",
            (module_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_student_results(student_id):
    with get_connection() as conn:
        student = conn.execute(
            "SELECT user_id, full_name, username, group_name FROM users "
            "WHERE user_id=? AND role='student'", (student_id,)
        ).fetchone()
        if student is None:
            raise ValueError("Student account not found.")
        rows = conn.execute(
            """SELECT m.module_name, m.coefficient, u.full_name AS teacher_name,
                      g.coursework_mark, g.exam_mark
               FROM modules m
               JOIN users u ON u.user_id=m.teacher_id
               LEFT JOIN grades g ON g.module_id=m.module_id AND g.student_id=?
               ORDER BY m.module_name""",
            (student_id,),
        ).fetchall()

    results = []
    weighted_sum = 0.0
    total_coeff = 0.0
    for row in rows:
        item = dict(row)
        item["module_average"] = calculate_module_average(
            item["coursework_mark"], item["exam_mark"]
        )
        if item["module_average"] is not None:
            weighted_sum += item["module_average"] * item["coefficient"]
            total_coeff += item["coefficient"]
        results.append(item)
    semester_average = weighted_sum / total_coeff if total_coeff else None
    return dict(student=dict(student), grades=results, semester_average=semester_average)


def get_students_for_teacher(teacher_id):
    """Return students and groups for teacher's assigned modules."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT DISTINCT s.user_id, s.username, s.full_name, s.email, s.group_name
               FROM users s
               JOIN grades g ON g.student_id=s.user_id
               JOIN modules m ON m.module_id=g.module_id
               WHERE s.role='student' AND m.teacher_id=?
               ORDER BY s.full_name""",
            (teacher_id,),
        ).fetchall()
    return [dict(row) for row in rows]
