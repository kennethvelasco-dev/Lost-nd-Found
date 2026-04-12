import re
import json
from email_validator import validate_email, EmailNotValidError
from zxcvbn import zxcvbn

class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

DISPOSABLE_DOMAINS = {
    "mailinator.com", "10minutemail.com", "temp-mail.org", "guerrillamail.com",
    "sharklasers.com", "dispostable.com", "yopmail.com", "duck.com"
}

def require_fields(data, required_fields):
    missing = [
        f for f in required_fields
        if f not in data or data[f] in (None, "", [])
    ]
    if missing:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing)}",
            400
        )

def validate_string(value, field_name, min_len=0, max_len=1000):
    if not isinstance(value, str):
        raise ValidationError(f"{field_name} must be a string", 400)
    if len(value) < min_len:
        raise ValidationError(f"{field_name} is too short (min {min_len})", 400)
    if len(value) > max_len:
        raise ValidationError(f"{field_name} is too long (max {max_len})", 400)
    return value

def validate_int(value, field_name, min_val=None, max_val=None):
    try:
        val = int(value)
        if min_val is not None and val < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}", 400)
        if max_val is not None and val > max_val:
            raise ValidationError(f"{field_name} must be at most {max_val}", 400)
        return val
    except (TypeError, ValueError):
        raise ValidationError(
            f"{field_name} must be an integer",
            400
        )

def validate_email_complex(email: str):
    """Multi-layer Email Validation (Format + MX + Disposable check)."""
    if not email: return None
    
    domain = email.split('@')[-1].lower()
    if domain in DISPOSABLE_DOMAINS:
        raise ValidationError("Disposable email addresses are not allowed.")

    try:
        # validate_email checks format AND MX record by default
        valid = validate_email(email, check_deliverability=True)
        return valid.normalized
    except EmailNotValidError as e:
        raise ValidationError(f"Invalid email: {str(e)}")

def validate_password_strength(password: str, username: str = None):
    """Enforce 8+ chars, complexity, and zxcvbn score >= 3."""
    if not password or len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")
    
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValidationError("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValidationError("Password must contain at least one number.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError("Password must contain at least one special character.")

    results = zxcvbn(password, user_inputs=[username] if username else [])
    if results['score'] < 3:
        feedback = results['feedback']['warning'] or "Password is too weak."
        raise ValidationError(f"Password strength too low: {feedback}")
    
    return True

def validate_found_item_id(item_id):
    return validate_int(item_id, "found_item_id", min_val=1)

def validate_claim_decision(decision):
    if decision not in {"approved", "rejected", "completed"}:
        raise ValidationError("Invalid decision", 400)
    return decision