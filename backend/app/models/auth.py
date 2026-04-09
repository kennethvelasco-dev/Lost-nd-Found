from .base import get_db_connection
from datetime import datetime, timezone

def save_verification_token_db(user_id, token):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET verification_token = ? WHERE id = ?", (token, user_id))
        conn.commit()
    finally:
        conn.close()

def verify_email_db(token):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE verification_token = ?", (token,))
        user = cursor.fetchone()
        
        if not user:
            return False
        
        cursor.execute(
            "UPDATE users SET is_email_verified = 1, verification_token = NULL WHERE id = ?",
            (user["id"],)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def block_token_db(jti):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO token_blocklist (jti, created_at) VALUES (?, ?)",
            (jti, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
    finally:
        conn.close()

def is_token_blocked_db(jti):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM token_blocklist WHERE jti = ?", (jti,))
        return cursor.fetchone() is not None
    finally:
        conn.close()

def update_login_attempts_db(user_id, attempts, lockout_until=None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET failed_login_attempts = ?, lockout_until = ? WHERE id = ?",
            (attempts, lockout_until, user_id)
        )
        conn.commit()
    finally:
        conn.close()

def reset_login_attempts_db(user_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET failed_login_attempts = 0, lockout_until = NULL WHERE id = ?",
            (user_id,)
        )
        conn.commit()
    finally:
        conn.close()

def get_user_by_email_db(email):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM users WHERE email = ?", (email,))
        return cursor.fetchone()
    finally:
        conn.close()

def save_pwd_reset_token_db(user_id, token, expires_at):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET reset_token = ?, reset_token_expires = ? WHERE id = ?",
            (token, expires_at, user_id)
        )
        conn.commit()
    finally:
        conn.close()

def get_user_by_reset_token_db(token):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE reset_token = ? AND reset_token_expires > ?",
            (token, datetime.now(timezone.utc).isoformat())
        )
        return cursor.fetchone()
    finally:
        conn.close()

def update_user_password_db(user_id, hashed_password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expires = ? WHERE id = ?",
            (hashed_password, datetime.now(timezone.utc).isoformat(), user_id)
        )
        conn.commit()
    finally:
        conn.close()
