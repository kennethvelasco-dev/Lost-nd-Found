from backend.models import (
    create_lost_item,
    create_found_item,
    get_published_found_items,
    ValidationError,
)
from backend.helpers.input_validation import validate_item_payload
from backend.models.items import search_items_db
from backend.helpers.formatter import format_item_description

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
    Combined service to get all reports and claims for a user.
    """
    from backend.models.items import get_user_reports_db
    from backend.models.claims import get_pending_claims
    
    reports = get_user_reports_db(user_id)
    all_claims = get_pending_claims()
    user_claims = [c for c in all_claims if str(c["user_id"]) == str(user_id)]
    
    return {
        "reports": reports,
        "claims": user_claims
    }, 200

def verify_report_service(report_id: int, entity_type: str, decision: str, reason: str, admin_username: str) -> tuple:
    """
    Service to approve/reject a report.
    """
    from backend.models.items import verify_report_db
    return verify_report_db(report_id, entity_type, decision, reason, admin_username)

def get_pending_reports_service() -> tuple:
    """Gets all reports awaiting approval."""
    from backend.models.base import get_db_connection
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT *, 'lost' as type FROM lost_items WHERE status = 'pending_approval'")
        lost = [dict(row) for row in cursor.fetchall()]
        cursor.execute("SELECT *, 'found' as type FROM found_items WHERE status = 'pending_approval'")
        found = [dict(row) for row in cursor.fetchall()]
        return {"pending": lost + found}, 200
    finally:
        conn.close()

def resolve_item_service(data: dict, admin_username: str) -> tuple:
    """Service to handle administrative item resolution."""
    from backend.helpers.input_validation import validate_int
    item_id = validate_int(data.get("item_id"), "item_id")
    recipient_name = data.get("owner_name", "Unknown")
    notes = data.get("handover_notes", "")
    
    from backend.models.items import resolve_item_db
    return resolve_item_db(item_id, recipient_name, notes, admin_username)
