from backend.helpers.user_helpers import create_user, get_user, verify_password
from backend.models import ValidationError
from flask_jwt_extended import create_access_token
from backend.helpers.input_validation import validate_registration_data

# Simple in-memory revoked tokens store
revoked_tokens = set()

def register_user(data: dict):
    """Handles user registration"""
    validate_registration_data(data)
    username = data.get("username")
    password = data.get("password")
    name = data.get("name")
    email = data.get("email")
    role = data.get("role")
    admin_id = data.get("admin_id")

    result = create_user(username, password, role, name, email, admin_id)

    if "user_id" in result:
        # Use string ID as identity, role in additional claims
        user_id_str = str(result["user_id"])
        token = create_access_token(
            identity=user_id_str,
            additional_claims={"role": role}
        )
        return {"access_token": token, "message": result["message"]}, 201

    raise ValidationError(result.get("error", "Registration failed"))


def login_user(data: dict):
    """Handles login"""
    if not data:
        raise ValidationError("Missing login data. Provide JSON body with 'username' and 'password'.")

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise ValidationError("Username and password are required for login.")

    user = get_user(username)
    if not user or not verify_password(password, user["password_hash"]):
        raise ValidationError("Invalid username or password.")

    # Use string ID as identity, role in additional claims
    user_id_str = str(user["id"])
    token = create_access_token(
        identity=user_id_str,
        additional_claims={"role": user["role"]}
    )
    return {"access_token": token, "message": "Login successful"}, 200

def refresh_token(user_id: str, role: str):
    """Generate a new access token"""
    new_access_token = create_access_token(
        identity=user_id,
        additional_claims={"role": role}
    )
    return {"access_token": new_access_token, "message": "Access token refreshed"}, 200

def logout_token(jti: str):
    """Revoke a JWT"""
    if not jti:
        raise ValidationError("No token provided to revoke.")
    revoked_tokens.add(jti)
    return {"message": "Logout successful, token revoked"}, 200

def is_token_revoked(jti: str) -> bool:
    return jti in revoked_tokens