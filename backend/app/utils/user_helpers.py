import sqlite3
import bcrypt
from datetime import datetime, timezone
from ..models.base import get_db_connection

# Hashing Helpers
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

# Database Helpers (Models)
def create_user_db(username, email, password_hash, role="user", name=None, verification_token=None):
    """Inserts a new user record into the database."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO users (username, email, password_hash, role, name, verification_token, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            username, email, password_hash, role, name, verification_token,
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_username(username: str):
    """Fetch a user by username."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_user_by_id(user_id: int):
    """Fetch a user by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def create_default_admin():
    """Initializes a default admin if it doesn't exist."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            pwd_hash = hash_password("AdminPass123!")
            cursor.execute(
                "INSERT INTO users (username, password_hash, role, name, admin_id, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("admin", pwd_hash, "admin", "System Admin", "ADM-001", datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
    finally:
        conn.close()
