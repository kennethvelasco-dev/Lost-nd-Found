from datetime import datetime, timezone
from .base import get_db_connection
from .validators import ValidationError, require_fields, validate_int
from .audit import log_action
from typing import Optional, Dict, Any

# Lost Items
def create_lost_item(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a lost item record with validation and logging."""
    try:
        # Validate required fields
        require_fields(data, ["category", "last_seen_location", "last_seen_datetime"])

        conn = get_db_connection()
        cursor = conn.cursor()

        import uuid

        cursor.execute("""
            INSERT INTO lost_items (
                report_id, category, item_type, last_seen_location,
                last_seen_datetime, public_description, private_details,
                main_picture, additional_picture_1, additional_picture_2,
                additional_picture_3, reporter_id, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), # Auto-generate report_id
            data["category"],
            data.get("item_type", "Unknown"),
            data["last_seen_location"],
            data["last_seen_datetime"],
            data.get("public_description"),
            data.get("private_details"),
            data.get("main_picture"),
            data.get("additional_picture_1"),
            data.get("additional_picture_2"),
            data.get("additional_picture_3"),
            data.get("reporter_id"),
            "lost", # Default status
            datetime.now(timezone.utc).isoformat()
        ))

        conn.commit()
        item_id = cursor.lastrowid

        # Log creation
        log_action("create", "lost_item", item_id, str(data.get("reporter_id", "system")))

        return {"message": "Lost item created successfully", "item_id": item_id}

    except ValidationError as ve:
        return {"error": ve.message}

    except Exception as e:
        import traceback
        return {"error": f"Database error: {str(e)}\n{traceback.format_exc()}"}

    finally:
        conn.close()

# Found Items
def create_found_item(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a found item record with validation and logging."""
    try:
        require_fields(data, ["category", "found_location", "found_datetime"])

        conn = get_db_connection()
        cursor = conn.cursor()

        import uuid

        cursor.execute("""
            INSERT INTO found_items (
                report_id, category, item_type, color, brand,
                found_location, found_datetime,
                public_description, private_details, main_picture,
                additional_picture_1, additional_picture_2, additional_picture_3,
                reporter_id, status, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()), # Auto-generate report_id
            data["category"],
            data.get("item_type", "Unknown"),
            data.get("color"),
            data.get("brand"),
            data["found_location"],
            data["found_datetime"],
            data.get("public_description"),
            data.get("private_details"),
            data.get("main_picture"),
            data.get("additional_picture_1"),
            data.get("additional_picture_2"),
            data.get("additional_picture_3"),
            data.get("reporter_id"),
            "found", # Default status
            datetime.now(timezone.utc).isoformat()
        ))

        conn.commit()
        item_id = cursor.lastrowid

        # Log creation
        log_action("create", "found_item", item_id, str(data.get("reporter_id", "system")))

        return {"message": "Found item created successfully", "item_id": item_id}

    except ValidationError as ve:
        return {"error": ve.message}

    except Exception as e:
        import traceback
        return {"error": f"Database error: {str(e)}\n{traceback.format_exc()}"}

    finally:
        conn.close()

# Get Found Items
def get_published_found_items() -> list[Dict[str, Any]]:
    """Return all published found items."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, report_id, category, item_type, color, brand,
               found_location, found_datetime, public_description,
               main_picture
        FROM found_items
        WHERE status = 'found'
        ORDER BY created_at DESC
    """)

    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items

# Get Found Item by ID
def get_found_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Return a found item by ID. Validates ID type."""
    try:
        validate_int(item_id, "item_id")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM found_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()

# Update Found Item Status
def update_found_item_status(item_id: int, new_status: str) -> Dict[str, Any]:
    """Update status of a found item with validation."""
    try:
        validate_int(item_id, "item_id")

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM found_items WHERE id = ?", (item_id,))
            if not cursor.fetchone():
                return {"error": "Item not found"}, 404

            cursor.execute("UPDATE found_items SET status = ? WHERE id = ?", (new_status, item_id))
            conn.commit()

        log_action("update_status", "found_item", item_id, "system")
        return {"message": "Found item status updated successfully"}, 200

    except ValidationError as ve:
        return {"error": ve.message}, ve.status_code
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}, 500
