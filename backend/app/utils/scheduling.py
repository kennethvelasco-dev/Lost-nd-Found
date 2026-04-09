from datetime import datetime, timezone
from ..models import ValidationError

def validate_future_date(date_str: str) -> str:
    """
    Validates that a provided date string is in the future.
    Expects ISO format string.
    """
    if not date_str:
        raise ValidationError("Date is required", 400)
        
    try:
        scheduled_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        raise ValidationError("Invalid date format. Use ISO 8601", 400)
        
    # Make sure we compare aware to aware datetimes
    if scheduled_date.tzinfo is None:
        scheduled_date = scheduled_date.replace(tzinfo=timezone.utc)
        
    now = datetime.now(timezone.utc)
    
    if scheduled_date < now:
        raise ValidationError("Scheduled date must be in the future", 400)
        
    return scheduled_date.isoformat()

def format_schedule_time(date_str: str) -> str:
    """Formats an ISO datestring into a human-readable format."""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except ValueError:
        return date_str
