import bcrypt
import logging
from datetime import datetime, timezone
from sqlalchemy import text
from ..extensions import db

logger = logging.getLogger(__name__)

# Hashing Helpers
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Check a password against its hash."""
    if not password or not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

# Database Helpers (Models)
def create_user_db(username, email, password_hash, role="user", name=None, verification_token=None):
    """Inserts a new user record into the database."""
    query = text("""
        INSERT INTO users (username, email, password_hash, role, name, verification_token, created_at)
        VALUES (:username, :email, :password_hash, :role, :name, :verification_token, :created_at)
        RETURNING id
    """)
    params = {
        "username": username,
        "email": email,
        "password_hash": password_hash,
        "role": role,
        "name": name,
        "verification_token": verification_token,
        "created_at": datetime.now(timezone.utc)
    }
    try:
        result = db.session.execute(query, params)
        row = result.fetchone()
        db.session.commit()
        return row[0] if row else None
    except Exception as e:
        db.session.rollback()
        logger.error(f"DB Error creating user: {str(e)}")
        return None

def get_user_by_username(username: str):
    """Fetch a user by username."""
    query = text("SELECT * FROM users WHERE username = :username")
    result = db.session.execute(query, {"username": username})
    row = result.fetchone()
    return dict(row._mapping) if row else None

def get_user_by_id(user_id: int):
    """Fetch a user by ID."""
    query = text("SELECT * FROM users WHERE id = :user_id")
    result = db.session.execute(query, {"user_id": user_id})
    row = result.fetchone()
    return dict(row._mapping) if row else None

def create_default_admin():
    """Initializes a default admin if it doesn't exist."""
    check_query = text("SELECT id FROM users WHERE username = :username")
    row = db.session.execute(check_query, {"username": "admin"}).fetchone()

    if not row:
        pwd_hash = hash_password("AdminPass123!")
        insert_query = text("""
            INSERT INTO users (username, email, password_hash, role, name, admin_id, created_at, is_email_verified) 
            VALUES (:username, :email, :password_hash, :role, :name, :admin_id, :created_at, :is_email_verified)
        """)
        db.session.execute(insert_query, {
            "username": "admin",
            "email": "admin8857@gmail.com",
            "password_hash": pwd_hash,
            "role": "admin",
            "name": "System Admin",
            "admin_id": "ADM-001",
            "created_at": datetime.now(timezone.utc),
            "is_email_verified": True
        })
        db.session.commit()
