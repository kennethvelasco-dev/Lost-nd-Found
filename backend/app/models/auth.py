from datetime import datetime, timezone
from sqlalchemy import text
from ..extensions import db


def save_verification_token_db(user_id, token):
    query = text("UPDATE users SET verification_token = :token WHERE id = :user_id")
    db.session.execute(query, {"token": token, "user_id": user_id})
    db.session.commit()


def verify_email_db(token):
    query = text("SELECT id FROM users WHERE verification_token = :token")
    user = db.session.execute(query, {"token": token}).fetchone()

    if not user:
        return False

    update_query = text(
        """
        UPDATE users 
        SET is_email_verified = TRUE, verification_token = NULL 
        WHERE id = :id
    """
    )
    db.session.execute(update_query, {"id": user.id})
    db.session.commit()
    return True


def block_token_db(jti):
    # 'ON CONFLICT DO NOTHING' for Postgres, equivalent to 'INSERT OR IGNORE'
    query = text(
        """
        INSERT INTO token_blocklist (jti, created_at) 
        VALUES (:jti, :created_at)
        ON CONFLICT (jti) DO NOTHING
    """
    )
    db.session.execute(query, {"jti": jti, "created_at": datetime.now(timezone.utc)})
    db.session.commit()


def is_token_blocked_db(jti):
    query = text("SELECT id FROM token_blocklist WHERE jti = :jti")
    result = db.session.execute(query, {"jti": jti}).fetchone()
    return result is not None


def update_login_attempts_db(user_id, attempts, lockout_until=None):
    query = text(
        """
        UPDATE users SET failed_login_attempts = :attempts, lockout_until = :lockout_until 
        WHERE id = :user_id
    """
    )
    db.session.execute(
        query,
        {"attempts": attempts, "lockout_until": lockout_until, "user_id": user_id},
    )
    db.session.commit()


def reset_login_attempts_db(user_id):
    query = text(
        """
        UPDATE users SET failed_login_attempts = 0, lockout_until = NULL 
        WHERE id = :user_id
    """
    )
    db.session.execute(query, {"user_id": user_id})
    db.session.commit()


def get_user_by_email_db(email):
    query = text("SELECT id, username FROM users WHERE email = :email")
    result = db.session.execute(query, {"email": email}).fetchone()
    return dict(result._mapping) if result else None


def save_pwd_reset_token_db(user_id, token, expires_at):
    query = text(
        """
        UPDATE users SET reset_token = :token, reset_token_expires = :expires_at 
        WHERE id = :user_id
    """
    )
    db.session.execute(
        query, {"token": token, "expires_at": expires_at, "user_id": user_id}
    )
    db.session.commit()


def get_user_by_reset_token_db(token):
    query = text(
        """
        SELECT id FROM users 
        WHERE reset_token = :token AND reset_token_expires > :now
    """
    )
    result = db.session.execute(
        query, {"token": token, "now": datetime.now(timezone.utc)}
    ).fetchone()
    return dict(result._mapping) if result else None


def update_user_password_db(user_id, hashed_password):
    query = text(
        """
        UPDATE users 
        SET password_hash = :hash, reset_token = NULL, reset_token_expires = NULL 
        WHERE id = :user_id
    """
    )
    db.session.execute(query, {"hash": hashed_password, "user_id": user_id})
    db.session.commit()
