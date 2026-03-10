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
