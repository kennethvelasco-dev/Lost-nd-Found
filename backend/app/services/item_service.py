from ..models import (
    create_lost_item,
    create_found_item,
    get_published_found_items,
    ValidationError,
)
from ..utils.input_validation import validate_item_payload
from ..models.items import search_items_db
from ..utils.formatter import format_item_description

def submit_lost_item(data: dict, user_id: str) -> tuple:
    """
    Validates and submits a lost item.
    """
    validate_item_payload(data, "lost")
    
    # Inject reporter_id from JWT
    data["reporter_id"] = user_id
    
    result = create_lost_item(data)
    if "error" in result:
        raise ValidationError(result["error"])
        
    return result, 201


def submit_found_item(data: dict, user_id: str) -> tuple:
    """
    Validates and submits a found item by a regular user.
    """
    validate_item_payload(data, "found")
    
    # Inject reporter_id from JWT
    data["reporter_id"] = user_id
    
    result = create_found_item(data)
    if "error" in result:
        raise ValidationError(result["error"])
        
    return result, 201

def submit_admin_found_item(data: dict, admin_id: str) -> tuple:
    """
    Validates and submits a found item by an admin.
    """
    validate_item_payload(data, "found")
    
    data["reporter_id"] = admin_id
    
    result = create_found_item(data)
    if "error" in result:
        raise ValidationError(result["error"])
        
    return result, 201


def get_found_items(limit=20, offset=0) -> tuple:
    """
    Returns published found items with formatted descriptions and pagination metadata.
    """
    items, total = get_published_found_items(limit, offset)
    for item in items:
        item["full_description"] = format_item_description(item)
    return {
        "items": items,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset
        }
    }, 200

def search_items_service(filters: dict) -> tuple:
    """
    Service for searching and filtering items with formatted descriptions and pagination.
    """
    items, total = search_items_db(filters)
    for item in items:
        item["full_description"] = format_item_description(item)
    return {
        "items": items,
        "pagination": {
            "total": total,
            "limit": filters.get("limit", 20),
            "offset": filters.get("offset", 0)
        }
    }, 200

def get_user_activities_service(user_id: str) -> tuple:
    """
    Combined service to get all reports and claims for a user, filtering out dismissed ones.
    """
    from ..models.items import get_user_reports_db
    from ..models.claims import get_claims_db
    
    reports = get_user_reports_db(user_id)
    user_claims = get_claims_db(user_id)
    
    return {
        "reports": reports,
        "claims": user_claims
    }, 200

def dismiss_activity_service(activity_id: int, activity_type: str, user_id: str) -> tuple:
    """Service to dismiss a report or claim."""
    if activity_type in ["lost", "found"]:
        from ..models.items import dismiss_report_db
        return dismiss_report_db(activity_id, activity_type, user_id)
    elif activity_type == "claim":
        from ..models.claims import dismiss_claim_db
        return dismiss_claim_db(activity_id, user_id)
    else:
        return {"error": "Invalid activity type"}, 400

def verify_report_service(report_id: int, entity_type: str, decision: str, reason: str, admin_username: str) -> tuple:
    """Service to approve/reject a report."""
    from ..models.items import verify_report_db
    return verify_report_db(report_id, entity_type, decision, reason, admin_username)

def get_pending_reports_service() -> tuple:
    """Gets all reports awaiting approval."""
    from ..models.items import get_pending_reports_db
    result = get_pending_reports_db()
    return result, 200

def resolve_item_service(data: dict, admin_username: str) -> tuple:
    """Service to handle administrative item resolution."""
    from ..models.validators import validate_int
    item_id = validate_int(data.get("item_id"), "item_id")
    recipient_name = data.get("owner_name", "Unknown")
    recipient_id = data.get("recipient_id") # Student ID
    claim_id = data.get("claim_id")
    notes = data.get("handover_notes", "")
    turnover_proof = data.get("turnover_proof")
    
    from ..models.items import resolve_item_db
    return resolve_item_db(item_id, recipient_name, notes, admin_username, claim_id=claim_id, recipient_id=recipient_id, turnover_proof=turnover_proof)

def get_item_detail_service(identifier: str) -> tuple:
    """Get full details of an item by its UUID or integer ID."""
    from ..models.items import get_item_universal_db
    item = get_item_universal_db(identifier)
    if not item:
        return {"error": "Item not found"}, 404
    return item, 200

def get_released_items_service(filters: dict) -> tuple:
    """Service to fetch released items with pagination and search."""
    from ..models.items import get_released_items_db
    limit = int(filters.get("limit", 20))
    offset = int(filters.get("offset", 0))
    query = filters.get("query")
    
    items, total = get_released_items_db(limit=limit, offset=offset, query=query)
    
    # Format descriptions for consistency
    from ..utils.formatter import format_item_description
    for item in items:
        item["full_description"] = format_item_description(item)
        
    return {
        "items": items,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset
        }
    }, 200
