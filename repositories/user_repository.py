from database import get_connection


def get_user_by_id(user_id):
    with get_connection() as conn:
        row = conn.execute(
            """SELECT user_id, username, role, full_name, email, group_name
               FROM users WHERE user_id=?""", (user_id,)
        ).fetchone()
    return dict(row) if row else None
