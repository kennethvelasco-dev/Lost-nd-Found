from backend.models.claims import (
    create_claim,
    ValidationError,
    require_fields,
    validate_found_item_id,
    link_claim_to_found_item,
    get_claim_by_id,
    schedule_pickup
)
from backend.models.items import get_published_found_items
from backend.services.scoring_service import compute_claim_score

def submit_claim(data: dict, user_id: str) -> tuple:
    """
    Validates and creates a claim. found_item_id can be null for general reports.
    """
    # For linked claims, we need these. For general reports, we might have different ones.
    # We'll allow general reports to have mostly 'answers' or similar metadata.
    
    if data.get("found_item_id"):
        require_fields(data, ["description", "declared_value", "receipt_proof"])
        validate_found_item_id(data["found_item_id"])
        
        # Validate declared_value
        try:
            val = float(data["declared_value"])
            if val < 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValidationError("declared_value must be a positive number", 400)

    # Inject claimant ID from JWT
    data["user_id"] = user_id
    
    # Store other metadata in 'answers' if not already there
    if "answers" not in data:
        data["answers"] = {
            "description": data.get("description"),
            "declared_value": data.get("declared_value"),
            "receipt_proof": data.get("receipt_proof"),
            "claimant_name": data.get("claimant_name"),
            "claimant_email": data.get("claimant_email"),
            "claimed_category": data.get("category"),
            "claimed_item_type": data.get("item_type"),
            "claimed_brand": data.get("brand"),
            "claimed_color": data.get("color"),
            "claimed_location": data.get("location"),
            "claimed_datetime": data.get("datetime")
        }

    result, status = create_claim(data)
    return result, status

def get_potential_matches_service(claim_id: int) -> tuple:
    """
    Finds potential found items for a claim based on scoring.
    """
    claim = get_claim_by_id(claim_id)
    if not claim:
        return {"error": "Claim not found"}, 404
        
    found_items = get_published_found_items()
    matches = []
    
    import json
    try:
        answers = json.loads(claim["answers"])
    except:
        answers = claim["answers"]

    for item in found_items:
        score_result = compute_claim_score(answers, item)
        if score_result["total"] > 0:
            item_data = dict(item)
            item_data["match_score"] = score_result["total"]
            item_data["match_breakdown"] = score_result["breakdown"]
            matches.append(item_data)
            
    # Sort by score descending
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {"matches": matches}, 200

def link_claim_service(claim_id: int, found_item_id: int) -> tuple:
    """Links a claim to a found item."""
    return link_claim_to_found_item(claim_id, found_item_id)

def schedule_pickup_service(claim_id: int, data: dict) -> tuple:
    """Schedules a pickup for an approved claim."""
    require_fields(data, ["pickup_datetime", "pickup_location"])
    return schedule_pickup(claim_id, data["pickup_datetime"], data["pickup_location"])
