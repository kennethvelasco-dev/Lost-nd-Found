import sqlite3
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from backend.models.base import get_db_connection

# User Helper Functions
def hash_password(password: str) -> str:
    """Hash a password using werkzeug."""
    return generate_password_hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Check a password against its hash."""
    return check_password_hash(password_hash, password)

def create_user(username: str, password: str, role: str = "user", name: str = None, email: str = None, admin_id: str = None):
    """Add a user to the users table safely and handle duplicates."""
    try:
        hashed_password = hash_password(password)
        conn = get_db_connection()  # already a connection
        c = conn.cursor()
        try:
            c.execute(
                """
                INSERT INTO users (username, password_hash, role, name, email, admin_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (username, hashed_password, role, name, email, admin_id, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
            user_id = c.lastrowid
            return {"user_id": user_id, "message": "User created successfully"}

        except sqlite3.IntegrityError:
            return {"error": "Username or Email already exists"}

        finally:
            conn.close()

    except sqlite3.OperationalError as e:
        return {"error": f"Database error: {str(e)}"}

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
    
def get_user(username: str):
    """Fetch a user by username. Returns dict or None."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, username, password_hash, role, name, email, admin_id, is_email_verified, created_at FROM users WHERE username = ?",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "username": row[1],
            "password_hash": row[2],
            "role": row[3],
            "name": row[4],
            "email": row[5],
            "admin_id": row[6],
            "is_email_verified": bool(row[7]),
            "created_at": row[8]
        }
    return None

def create_default_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if cursor.fetchone() is None: 
        password_hash = hash_password("AdminPass123!")
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, name, admin_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("admin", password_hash, "admin", "System Admin", "ADM-001", datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
    conn.close()
