from database.database import get_connection


def get_grades_for_student(student_id):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT g.*, m.module_name, m.coefficient
               FROM grades g JOIN modules m ON m.module_id=g.module_id
               WHERE g.student_id=? ORDER BY m.module_name""",
            (student_id,),
        ).fetchall()
    return [dict(row) for row in rows]
