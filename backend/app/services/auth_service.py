import uuid
from datetime import datetime, timezone, timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity
from ..models.base import get_db_connection
from ..models.validators import (
    ValidationError, 
    require_fields, 
    validate_email_complex, 
    validate_password_strength
)
from ..utils.user_helpers import create_user, get_user, verify_password

def register_user(data: dict):
    """Handles user registration with email verification token generation."""
    require_fields(data, ["username", "password", "role"])
    
    username = data.get("username")
    password = data.get("password")
    name = data.get("name")
    email = data.get("email")
    role = data.get("role")
    admin_id = data.get("admin_id")

    # 1. Advanced Validation
    validate_password_strength(password, username)
    normalized_email = None
    if email:
        normalized_email = validate_email_complex(email)

    # 2. Generate Verification Token
    verification_token = str(uuid.uuid4())

    # 3. Create User in DB
    result = create_user(
        username=username, 
        password=password, 
        role=role, 
        name=name, 
        email=normalized_email, 
        admin_id=admin_id
    )

    if "user_id" in result:
        user_id = result["user_id"]
        # Save verification token to DB
        _save_verification_token(user_id, verification_token)
        
        # 4. Mock Email Sending
        if normalized_email:
            _mock_send_verification_email(normalized_email, verification_token)

        # Generate initial access token (or wait for verification depending on policy)
        # For this app, we'll allow login but maybe restrict actions if not verified.
        # However, the user asked for "Email verification flow", so we'll return the token for testing.
        user_id_str = str(user_id)
        token = create_access_token(
            identity=user_id_str,
            additional_claims={"role": role}
        )
        return {
            "access_token": token, 
            "message": "Registration successful. Please verify your email.",
            "debug_verification_token": verification_token # For easier testing
        }, 201

    raise ValidationError(result.get("error", "Registration failed"))

def login_user(data: dict):
    """Handles login with account lockout and session security."""
    require_fields(data, ["username", "password"])

    username = data.get("username")
    password = data.get("password")

    user = get_user(username)
    if not user:
        raise ValidationError("Invalid username or password.")

    # 1. Check Account Lockout
    now = datetime.now(timezone.utc)
    lockout_until_str = user.get("lockout_until")
    if lockout_until_str:
        lockout_until = datetime.fromisoformat(lockout_until_str)
        if now < lockout_until:
            wait_time = int((lockout_until - now).total_seconds() / 60)
            raise ValidationError(f"Account is locked. Please try again in {max(1, wait_time)} minutes.", 403)

    # 2. Verify Password
    if not verify_password(password, user["password_hash"]):
        _handle_failed_login(user["id"], user.get("failed_login_attempts", 0))
        raise ValidationError("Invalid username or password.")

    # 3. Success - Reset attempts
    _reset_login_attempts(user["id"])

    user_id_str = str(user["id"])
    now_ts = int(now.timestamp())
    
    additional_claims = {
        "role": user["role"],
        "auth_time": now_ts
    }
    
    # Stricter lifetimes for Admins
    access_expiry = timedelta(minutes=10) if user["role"] == "admin" else timedelta(minutes=15)
    refresh_expiry = timedelta(minutes=30) if user["role"] == "admin" else timedelta(days=7)
    
    access_token = create_access_token(
        identity=user_id_str,
        additional_claims=additional_claims,
        expires_delta=access_expiry
    )
    refresh_token = create_refresh_token(
        identity=user_id_str,
        additional_claims=additional_claims,
        expires_delta=refresh_expiry
    )
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "user": {
            "username": user["username"],
            "role": user["role"],
            "name": user.get("name", ""),
            "is_verified": user.get("is_email_verified", False)
        },
        "message": "Login successful"
    }, 200

def refresh_token_service(user_id: str, role: str):
    """RTR implementation with Absolute Timeout check."""
    claims = get_jwt()
    auth_time = claims.get("auth_time")
    
    if auth_time:
        if int(datetime.now(timezone.utc).timestamp()) - auth_time > 86400: # 24h
            raise ValidationError("Absolute session timeout reached. Please log in again.")

    access_expiry = timedelta(minutes=10) if role == "admin" else timedelta(minutes=15)
    refresh_expiry = timedelta(minutes=30) if role == "admin" else timedelta(days=7)

    new_access_token = create_access_token(
        identity=user_id,
        additional_claims={"role": role, "auth_time": auth_time},
        expires_delta=access_expiry
    )
    new_refresh_token = create_refresh_token(
        identity=user_id,
        additional_claims={"role": role, "auth_time": auth_time},
        expires_delta=refresh_expiry
    )
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }, 200

def verify_email_service(token: str):
    """Verifies a user's email using the provided token."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE verification_token = ?", (token,))
        user = cursor.fetchone()
        
        if not user:
            raise ValidationError("Invalid or expired verification token.")
        
        cursor.execute(
            "UPDATE users SET is_email_verified = 1, verification_token = NULL WHERE id = ?",
            (user["id"],)
        )
        conn.commit()
        return {"message": "Email verified successfully"}, 200
    finally:
        conn.close()

def logout_token(jti: str):
    """Revoke a token."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO token_blocklist (jti, created_at) VALUES (?, ?)",
            (jti, datetime.now(timezone.utc).isoformat())
        )
        conn.commit()
        return {"message": "Logout successful"}, 200
    finally:
        conn.close()

def is_token_revoked(jti: str) -> bool:
    """Check blocklist."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM token_blocklist WHERE jti = ?", (jti,))
        return cursor.fetchone() is not None
    finally:
        conn.close()

# Internal Helpers
def _save_verification_token(user_id, token):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET verification_token = ? WHERE id = ?", (token, user_id))
        conn.commit()
    finally:
        conn.close()

def _mock_send_verification_email(email, token):
    """Logs the verification link to the console (Mock)"""
    # In production, this would use Flask-Mail or an API like SendGrid
    verification_link = f"http://localhost:5000/api/auth/verify-email?token={token}"
    print("\n" + "="*50)
    print(f"MOCK EMAIL SENT TO: {email}")
    print(f"SUBJECT: Verify your Lost & Found Account")
    print(f"LINK: {verification_link}")
    print("="*50 + "\n")

def _handle_failed_login(user_id, current_attempts):
    """Increment failed attempts and lock if threshold reached."""
    new_attempts = current_attempts + 1
    lockout_until = None
    
    if new_attempts >= 5:
        # 15 minute lockout
        lockout_until = (datetime.now(timezone.utc) + timedelta(minutes=15)).isoformat()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET failed_login_attempts = ?, lockout_until = ? WHERE id = ?",
            (new_attempts, lockout_until, user_id)
        )
        conn.commit()
    finally:
        conn.close()

def _reset_login_attempts(user_id):
    """Reset attempts on successful login."""
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