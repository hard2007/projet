import hashlib
import hmac
import secrets
from database import get_connection


def hash_password(password: str) -> str:
    """Hash password with PBKDF2-HMAC-SHA256. Never store plain-text passwords."""
    if not password:
        raise ValueError("Password cannot be empty.")
    salt = secrets.token_bytes(16)
    rounds = 310_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return f"pbkdf2_sha256${rounds}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, rounds, salt_hex, expected = stored_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(rounds)
        ).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def authenticate(username: str, password: str):
    with get_connection() as conn:
        row = conn.execute(
            """SELECT user_id, username, password_hash, role, full_name, email, group_name
               FROM users WHERE username = ?""",
            (username.strip(),),
        ).fetchone()
    if row is None or not verify_password(password, row["password_hash"]):
        return None
    user = dict(row)
    user.pop("password_hash", None)
    return user


def create_user(username, password, role, full_name, email=None, group_name=None):
    """Create a student or teacher account; use only for trusted account setup."""
    username = username.strip()
    full_name = full_name.strip()
    if role not in ("student", "teacher"):
        raise ValueError("Role must be 'student' or 'teacher'.")
    if not username or not full_name:
        raise ValueError("Username and full name are required.")
    if role == "teacher":
        group_name = None
    elif group_name is not None:
        group_name = group_name.strip() or None

    password_hash = hash_password(password)
    with get_connection() as conn:
        cur = conn.execute(
            """INSERT INTO users
               (username, password_hash, role, full_name, email, group_name)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (username, password_hash, role, full_name, email or None, group_name),
        )
        return cur.lastrowid
