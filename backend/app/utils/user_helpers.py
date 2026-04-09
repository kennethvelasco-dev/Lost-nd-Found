import sqlite3
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.base import get_db_connection

import bcrypt

# User Helper Functions
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Check a password against its hash (handles both bcrypt and legacy werkzeug)."""
    if not password or not password_hash:
        return False
    
    # Bcrypt hashes typically start with $2
    if password_hash.startswith('$2'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    
    # Legacy fallback for werkzeug hashes
    try:
        from werkzeug.security import check_password_hash
        return check_password_hash(password_hash, password)
    except Exception:
        return False
    
def generate_password_hash_legacy(password: str) -> str:
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

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
    try:
        c = conn.cursor()
        c.execute(
            """SELECT id, username, password_hash, role, name, email, admin_id, 
                      is_email_verified, failed_login_attempts, lockout_until, created_at 
               FROM users WHERE username = ?""",
            (username,)
        )
        row = c.fetchone()
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
                "failed_login_attempts": row[8],
                "lockout_until": row[9],
                "created_at": row[10]
            }
        return None
    finally:
        conn.close()

def create_default_admin():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if cursor.fetchone() is None: 
            password_hash = hash_password("AdminPass123!")
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, name, admin_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("admin", password_hash, "admin", "System Admin", "ADM-001", datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
    finally:
        conn.close()
