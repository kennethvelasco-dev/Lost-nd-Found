from backend.models import (
    create_claim,
    ValidationError,
    require_fields,
    validate_found_item_id,
)

def submit_claim(data: dict, claimed_by: str) -> tuple:
    """
    Validates and creates a claim.
    
    Args:
        data (dict): Raw input data from route
        claimed_by (str): username from JWT

    Returns:
        tuple: (result dict, HTTP status)
    """
    require_fields(data, ["found_item_id", "description", "declared_value"])
    validate_found_item_id(data["found_item_id"])
    
    # Validate types
    if not isinstance(data.get("declared_value"), (int, float)):
        return {"error": "declared_value must be a number"}, 400
        
    if data["declared_value"] < 0:
         return {"error": "declared_value must be positive"}, 400

    # Receipt validation (strict: must be present)
    if not data.get("receipt_proof"):
         return {"error": "receipt_proof is required"}, 400

    data["claimed_by"] = claimed_by
    result, status = create_claim(data)
    
    return result, status
