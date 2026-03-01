from backend.models import (
    create_lost_item,
    create_found_item,
    get_published_found_items,
    ValidationError,
)
from backend.helpers.input_validation import validate_item_payload
from backend.models.items import search_items_db

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
    Admins might have different defaults or logging.
    """
    validate_item_payload(data, "found")
    
    data["reporter_id"] = admin_id
    # Admin reports might have different status or priority in future
    
    result = create_found_item(data)
    if "error" in result:
        raise ValidationError(result["error"])
        
    return result, 201


def get_found_items() -> tuple:
    """
    Returns published found items.
    """
    return get_published_found_items(), 200

def search_items_service(filters: dict) -> tuple:
    """
    Service for searching and filtering items.
    Filters can include category, item_type, color, brand, status, and query.
    """
    items = search_items_db(filters)
    return items, 200
