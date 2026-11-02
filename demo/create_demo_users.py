"""Seed the local database with fictional users and sample academic data."""
from pathlib import Path

from database.database import get_connection, initialize_database
from services.auth_service import create_user, hash_password

TEACHER_PASSWORD = "TeacherDemo123!"
STUDENT_PASSWORD = "StudentDemo123!"

TEACHERS = [
    ("teacher1", "Samira Bennani"),
    ("teacher2", "Youssef Amrani"),
    ("teacher3", "Nadia El Fassi"),
    ("teacher4", "Karim Alaoui"),
    ("teacher5", "Salma Idrissi"),
]

STUDENTS = [
    "Amina El Idrissi", "Yassine Benali", "Salma Amrani", "Omar El Fassi",
    "Lina Bennani", "Mehdi Alaoui", "Nour Eddine Tazi", "Sara Chraibi",
    "Hamza Berrada", "Meryem Zahraoui", "Adam Lahlou", "Imane Rami",
    "Anas El Mansouri", "Hiba Kettani", "Soufiane Ouazzani",
    "Aya Benjelloun", "Reda Moutaouakil", "Kenza Filali", "Ilyas Naciri",
    "Ghita Bennis", "Bilal Ait Lahcen", "Maha Sefrioui", "Rayan Tahiri",
    "Chaimae Laghmari", "Amine Skalli", "Yasmine Bennouna", "Zakaria Fikri",
    "Dounia El Gharbi", "Ismail Chafik", "Rim El Khatib",
    "Mouad Boulahya", "Sanae El Ouardi", "Ayoub Mernissi", "Farah Lamrani",
    "Taha Zemmouri", "Mariam Belhaj", "Anouar El Khattabi", "Nisrine Fassi",
    "Bilal Choukri", "Loubna Azzouzi", "Ibrahim Benkirane", "Malak Rachidi",
    "Hamza El Amrani", "Siham El Hachimi", "Younes Bennis", "Nada Bakkali",
    "Khalid El Idrissi", "Rania Oukacha", "Anas El Alami", "Mouna Tazi",
    "Sami Belkacem", "Hajar El Mansouri", "Ziad Benomar", "Salma El Khatib",
    "Fouad Lahlou", "Lina Berrada", "Marouane Chraibi", "Dina Alaoui",
    "Rachid Ait Omar", "Meryem Benjelloun",
]

MODULES = [
    ("Python", 3, "teacher1"),
    ("Mathematics", 4, "teacher2"),
    ("Databases", 3, "teacher3"),
    ("Networks", 3, "teacher4"),
    ("Algorithms", 4, "teacher5"),
    ("English", 2, "teacher1"),
]


def ensure_user(username, password, role, full_name, email=None, group_name=None):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT user_id FROM users WHERE username = ?", (username,)
        ).fetchone()
    if row:
        user_id = row["user_id"]
        with get_connection() as conn:
            conn.execute(
                """UPDATE users
                   SET password_hash=?, role=?, full_name=?, email=?, group_name=?
                   WHERE user_id=?""",
                (
                    hash_password(password),
                    role,
                    full_name,
                    email,
                    group_name,
                    user_id,
                ),
            )
        return user_id
    return create_user(username, password, role, full_name, email, group_name)


def ensure_module(module_name, coefficient, teacher_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT module_id FROM modules WHERE module_name = ?", (module_name,)
        ).fetchone()
    if row:
        return row["module_id"]
    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO modules (module_name, coefficient, teacher_id)
               VALUES (?, ?, ?)""",
            (module_name, coefficient, teacher_id),
        )
        return cursor.lastrowid


def write_credentials_file(teacher_accounts, student_accounts):
    lines = [
        "LOCAL DEMO ACCOUNTS ONLY - fictional sample data",
        "Do not use these credentials or this database for real student information.",
        "Running python -m demo.create_demo_users resets passwords for these demo usernames.",
        "",
        "TEACHERS",
        "Username | Password | Name",
    ]
    lines.extend(
        f"{username} | {TEACHER_PASSWORD} | {full_name}"
        for username, full_name, _ in teacher_accounts
    )
    lines.extend(["", "STUDENTS", "Username | Password | Name | Group"])
    lines.extend(
        f"{username} | {STUDENT_PASSWORD} | {full_name} | {group_name}"
        for username, full_name, group_name, _ in student_accounts
    )
    credentials_path = Path(__file__).resolve().with_name("DEMO_CREDENTIALS.txt")
    credentials_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    initialize_database()

    teacher_accounts = []
    teacher_ids = {}
    for username, full_name in TEACHERS:
        user_id = ensure_user(
            username,
            TEACHER_PASSWORD,
            "teacher",
            full_name,
            f"{username}@example.test",
        )
        teacher_ids[username] = user_id
        teacher_accounts.append((username, full_name, user_id))

    student_accounts = []
    for index, full_name in enumerate(STUDENTS):
        username = f"student{index + 1}"
        group_name = f"G{index // 15 + 1}"
        user_id = ensure_user(
            username,
            STUDENT_PASSWORD,
            "student",
            full_name,
            f"{username}@example.test",
            group_name,
        )
        student_accounts.append((username, full_name, group_name, user_id))

    module_ids = {}
    for module_name, coefficient, teacher_username in MODULES:
        module_ids[module_name] = ensure_module(
            module_name, coefficient, teacher_ids[teacher_username]
        )

    with get_connection() as conn:
        for student_index, (_, _, _, student_id) in enumerate(student_accounts):
            for module_index, module_name in enumerate(module_ids):
                coursework_mark = 10 + (student_index * 3 + module_index * 2) % 11
                exam_mark = 10 + (student_index * 5 + module_index * 3) % 11
                conn.execute(
                    """INSERT OR IGNORE INTO grades
                       (student_id, module_id, coursework_mark, exam_mark)
                       VALUES (?, ?, ?, ?)""",
                    (
                        student_id,
                        module_ids[module_name],
                        coursework_mark,
                        exam_mark,
                    ),
                )

    write_credentials_file(teacher_accounts, student_accounts)
    print("Demo data ready: 60 students, 5 teachers, 4 groups, 6 modules.")
    print("Sample grades are available for every student and module.")
    print("Credentials: demo/DEMO_CREDENTIALS.txt")
    print("These accounts are for local testing only; do not use real student data.")


if __name__ == "__main__":
    main()
