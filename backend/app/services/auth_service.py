import time
import secrets
import bcrypt
import logging
from sqlalchemy import text
from flask import current_app
from datetime import datetime, timedelta, timezone
from ..utils.email_service import send_verification_email, send_password_reset_email
from ..extensions import limiter
from ..extensions import db
from ..models.validators import ValidationError


def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    """Verifies a password against its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def register_user(data: dict) -> tuple:
    """
    Service to handle user registration with security checks.
    """
    from ..utils.user_helpers import create_user_db, get_user_by_username

    username = data.get("username", "").strip()
    email = data.get("email", "").lower().strip()
    password = data.get("password", "")
    # Force self-registered accounts to be regular users
    role = "user"
    name = data.get("name", "").strip()

    if not username or not password:
        raise ValidationError("Username and password are required")

    if get_user_by_username(username):
        raise ValidationError("Username already exists")

    # Enforce password strength
    from ..models.validators import validate_password_strength

    validate_password_strength(password, username)

    hashed_password = hash_password(password)

    # Generate verification token
    verification_token = secrets.token_urlsafe(32)

    user_id = create_user_db(
        username=username,
        email=email,
        password_hash=hashed_password,
        role=role,
        name=name,
        verification_token=verification_token,
    )

    if not user_id:
        raise ValidationError("Could not create user", 500)

    # In Zero-Cost strategy, this logs to console
    send_verification_email(email, verification_token)

    # Auto-verify the account
    db.session.execute(
        text("UPDATE users SET is_email_verified = TRUE WHERE id = :id"),
        {"id": user_id},
    )
    db.session.commit()

    return {"message": "User registered successfully."}, 201


def login_user(data: dict) -> tuple:
    """
    Service to handle user login with lockout protection.
    """
    from ..utils.user_helpers import get_user_by_username
    from flask_jwt_extended import create_access_token, create_refresh_token

    username = data.get("username", "").strip()
    password = data.get("password", "")

    user = get_user_by_username(username)
    if not user:
        raise ValidationError("Invalid username or password", 401)

    # Check lockout
    if user.get("lockout_until"):
        lockout_time = datetime.fromisoformat(user["lockout_until"])
        if lockout_time.tzinfo is None:
            lockout_time = lockout_time.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) < lockout_time:
            raise ValidationError(
                "Account is locked due to multiple failed attempts. Try again later.",
                403,
            )

    if not check_password(password, user["password_hash"]):
        _handle_failed_login(user["id"], user.get("failed_login_attempts", 0))
        raise ValidationError("Invalid username or password", 401)

    # Check verification
    if not user.get("is_email_verified"):
        raise ValidationError("Please verify your account before logging in.", 403)

    # Create tokens
    # 'auth_time' is the absolute login time for session duration enforcement
    auth_time = int(time.time())
    additional_claims = {"role": user["role"], "auth_time": auth_time}
    access_token = create_access_token(
        identity=str(user["id"]), additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(
        identity=str(user["id"]), additional_claims=additional_claims
    )

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "name": user["name"],
        },
    }, 200


def refresh_token_service(user_id: str, role: str, auth_time: int) -> tuple:
    """Generates a new access/refresh token pair (RTR) while preserving auth_time."""
    from flask_jwt_extended import create_access_token, create_refresh_token

    additional_claims = {"role": role, "auth_time": auth_time}
    access_token = create_access_token(
        identity=user_id, additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(
        identity=user_id, additional_claims=additional_claims
    )

    return {"access_token": access_token, "refresh_token": refresh_token}, 200


def verify_email_service(token: str):
    """Verifies a user's email using the provided token."""
    from ..models.auth import verify_email_db

    if verify_email_db(token):
        return {"message": "Email verified successfully"}, 200
    raise ValidationError("Invalid or expired verification token.")


def logout_token(jti: str):
    """Revoke a token."""
    from ..models.auth import block_token_db

    block_token_db(jti)
    return {"message": "Logout successful"}, 200


def is_token_revoked(jti: str) -> bool:
    """Check blocklist."""
    from ..models.auth import is_token_blocked_db

    return is_token_blocked_db(jti)


def request_password_reset(email: str):
    """Generates a reset token and logs a reset link to the console."""
    normalized_email = email.lower().strip()

    from ..models.auth import get_user_by_email_db, save_pwd_reset_token_db

    user = get_user_by_email_db(normalized_email)

    if not user:
        # Avoid user enumeration - return success even if user not found
        return {
            "message": "If an account exists with this email, a reset link has been sent."
        }, 200

    reset_token = secrets.token_urlsafe(32)
    expiry_mins = current_app.config.get("RESET_TOKEN_EXPIRY_MINUTES", 60)
    expires_at = (
        datetime.now(timezone.utc) + timedelta(minutes=expiry_mins)
    ).isoformat()

    save_pwd_reset_token_db(user["id"], reset_token, expires_at)

    # In 'Zero-Cost' strategy, this logs to console
    send_password_reset_email(normalized_email, reset_token)

    return {
        "message": "If an account exists with this email, a reset link has been sent."
    }, 200


def reset_password(token: str, new_password: str):
    """Validates reset token and updates the password."""
    from ..models.auth import get_user_by_reset_token_db, update_user_password_db

    user = get_user_by_reset_token_db(token)

    if not user:
        raise ValidationError("Invalid or expired reset token.")

    # Validate complexity
    from ..models.validators import validate_password_strength

    validate_password_strength(new_password)

    new_hash = hash_password(new_password)
    update_user_password_db(user["id"], new_hash)

    return {"message": "Password reset successfully. You can now log in."}, 200


# Internal Helpers
def _save_verification_token(user_id, token):
    from ..models.auth import save_verification_token_db

    save_verification_token_db(user_id, token)


def _handle_failed_login(user_id, current_attempts):
    """Increment failed attempts and lock if threshold reached."""
    new_attempts = (current_attempts or 0) + 1
    lockout_until = None

    if new_attempts >= 5:
        # 15 minute lockout
        lockout_until = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()

    from ..models.auth import update_login_attempts_db

    update_login_attempts_db(user_id, new_attempts, lockout_until)


def _reset_login_attempts(user_id):
    """Reset attempts on successful login."""
    from ..models.auth import reset_login_attempts_db

    reset_login_attempts_db(user_id)
