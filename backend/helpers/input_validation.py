import re
from backend.models.validators import ValidationError, require_fields

def validate_email(email: str) -> bool:
    """Basic email format validation."""
    if not email:
        raise ValidationError("Email is required", 400)
    
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format", 400)
    return True

def validate_password_strength(password: str) -> bool:
    """Validates password strength."""
    if not password:
        raise ValidationError("Password is required", 400)
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long", 400)
    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain at least one uppercase letter", 400)
    if not any(c.islower() for c in password):
        raise ValidationError("Password must contain at least one lowercase letter", 400)
    if not any(c.isdigit() for c in password):
        raise ValidationError("Password must contain at least one number", 400)
    return True

def validate_registration_data(data: dict) -> bool:
    """Validates registration data."""
    if not data:
        raise ValidationError("Missing registration data", 400)
    require_fields(data, ["username", "password", "name", "email", "role"])
    
    role = data.get("role")
    validate_password_strength(data["password"])
    validate_email(data["email"])
    
    if role not in ["user", "admin"]:
        raise ValidationError("Role must be either 'user' or 'admin'", 400)
    
    if role == "admin" and not data.get("admin_id"):
        raise ValidationError("Admin ID is required for administrative accounts", 400)
        
    return True

def validate_item_payload(data: dict, mode: str) -> bool:
    """Validates lost/found item payload."""
    if not data:
        raise ValidationError(f"Missing {mode} item data", 400)

    common_required = ["category", "item_type", "public_description"]
    
    if mode == "lost":
        require_fields(data, common_required + ["last_seen_location", "last_seen_datetime", "private_details"])
        date_field = "last_seen_datetime"
    elif mode == "found":
        require_fields(data, common_required + ["found_location", "found_datetime"])
        date_field = "found_datetime"
    else:
        raise ValidationError("Invalid item report mode", 400)

    try:
        from datetime import datetime
        datetime.fromisoformat(data[date_field].replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise ValidationError(f"Invalid datetime format for {date_field}. Use ISO format.", 400)

    pic_fields = ["main_picture", "additional_picture_1", "additional_picture_2", "additional_picture_3"]
    for field in pic_fields:
        url = data.get(field)
        if url and not (url.startswith("http://") or url.startswith("https://") or url.startswith("/") or url.startswith("data:")):
            raise ValidationError(f"Invalid URL for {field}", 400)

    return True

def validate_claim_payload(data: dict) -> bool:
    """Validates claim submission payload."""
    if not data:
        raise ValidationError("Missing claim data", 400)
    require_fields(data, ["found_item_id", "description", "receipt_proof"])
    
    if "declared_value" in data:
        try:
            val = float(data["declared_value"])
            if val < 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValidationError("Declared value must be a positive number", 400)
            
    return True
