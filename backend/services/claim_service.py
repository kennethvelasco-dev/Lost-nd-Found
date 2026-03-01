from backend.models import (
    create_claim,
    ValidationError,
    require_fields,
    validate_found_item_id,
)

def submit_claim(data: dict, user_id: str) -> tuple:
    """
    Validates and creates a claim.
    """
    require_fields(data, ["found_item_id", "description", "declared_value", "receipt_proof"])
    validate_found_item_id(data["found_item_id"])
    
    # Validate declared_value is a number
    try:
        val = float(data["declared_value"])
        if val < 0:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("declared_value must be a positive number", 400)

    # Inject claimant ID from JWT
    data["claimed_by"] = user_id
    
    result, status = create_claim(data)
    if "error" in result:
        raise ValidationError(result["error"])
        
    return result, status
