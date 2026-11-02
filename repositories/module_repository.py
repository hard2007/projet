from database.database import get_connection


def get_module(module_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM modules WHERE module_id=?", (module_id,)).fetchone()
    return dict(row) if row else None
