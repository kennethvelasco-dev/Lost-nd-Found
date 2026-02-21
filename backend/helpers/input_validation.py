import re
from backend.models.validators import ValidationError, require_fields

def validate_email(email: str) -> bool:
    """Basic email format validation."""
    if not email:
        raise ValidationError("Email is required", 400)
    
    # Simple regex for email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format", 400)
    return True

def validate_password_strength(password: str) -> bool:
    """
    Validates password strength.
    Requires at least 8 chars, one uppercase, one lowercase, one number.
    """
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
    """
    Validates registration data for user-friendly error messages.
    """
    if not data:
        raise ValidationError("Missing registration data", 400)

    require_fields(data, ["username", "password"])
    
    validate_password_strength(data["password"])
    
    # If email is provided, validate it
    if "email" in data and data["email"]:
        validate_email(data["email"])
        
    return True

def validate_claim_payload(data: dict) -> bool:
    """
    Validates claim submission payload.
    """
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
