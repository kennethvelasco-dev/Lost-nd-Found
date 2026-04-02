from datetime import datetime, timezone
from .base import get_db_connection
from .validators import ValidationError, require_fields, validate_int
from .audit import log_action
from typing import Optional, Dict, Any

# Lost Items
def create_lost_item(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a lost item record with validation and logging."""
    conn = get_db_connection()
    try:
        # Validate required fields
        require_fields(data, ["category", "last_seen_location", "last_seen_datetime"])

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
            "pending_approval", # Default status for user reports
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
    conn = get_db_connection()
    try:
        require_fields(data, ["category", "found_location", "found_datetime"])

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
            "pending_approval", # Default status
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
def get_published_found_items(limit=20, offset=0) -> tuple[list[Dict[str, Any]], int]:
    """Return all published found items with pagination."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Get total count (search for 'lost' status for available items)
        cursor.execute("SELECT COUNT(*) FROM found_items WHERE status = 'lost'")
        total_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT id, report_id, category, item_type, color, brand,
                   found_location, found_datetime, public_description,
                   main_picture
            FROM found_items
            WHERE status = 'lost'
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        items = [dict(row) for row in cursor.fetchall()]
        return items, total_count
    finally:
        conn.close()

# Get Found Item by ID
def get_found_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    """Return a found item by ID. Validates ID type."""
    conn = get_db_connection()
    try:
        validate_int(item_id, "item_id")

        cursor = conn.cursor()

        cursor.execute("SELECT * FROM found_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        return dict(row)
    finally:
        conn.close()

# Verify Report (Admin)
def verify_report_db(report_id, entity_type, decision, reason, admin_username):
    """Approve or reject a report. entity_type is 'lost' or 'found'."""
    table = "lost_items" if entity_type == "lost" else "found_items"
    # User's Terminology: 
    # Approved Found -> 'lost' (Available to claim)
    # Approved Lost -> 'reported_lost' (Private report)
    # Released -> 'found' (Finished)
    approved_status = "reported_lost" if entity_type == "lost" else "lost"
    new_status = approved_status if decision == "approved" else "rejected"

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table} SET status = ?, rejection_reason = ? WHERE id = ?", (new_status, reason, report_id))
        
        if cursor.rowcount == 0:
            return {"error": f"Report ID {report_id} not found in {entity_type} items."}, 404

        conn.commit()
        log_action(f"verify_report_{decision}", entity_type, report_id, admin_username, notes=reason)
        return {"message": f"Report {decision} successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        conn.close()

# Get User Reports
def get_user_reports_db(user_id):
    """Retrieve all reports (lost and found) for a specific user, excluding dismissed ones."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *, 
                   last_seen_datetime AS incident_date, 
                   created_at AS report_date,
                   'lost' as type 
            FROM lost_items 
            WHERE reporter_id = ? AND is_dismissed = 0
        """, (user_id,))
        lost = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute("""
            SELECT *, 
                   found_datetime AS incident_date, 
                   created_at AS report_date,
                   'found' as type 
            FROM found_items 
            WHERE reporter_id = ? AND is_dismissed = 0
        """, (user_id,))
        found = [dict(row) for row in cursor.fetchall()]
        
        return lost + found
    finally:
        conn.close()

def dismiss_report_db(report_id, entity_type, user_id):
    """Mark a report as dismissed for the user."""
    table = "lost_items" if entity_type == "lost" else "found_items"
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {table} SET is_dismissed = 1 WHERE id = ? AND reporter_id = ?", (report_id, user_id))
        conn.commit()
        return {"message": "Report dismissed successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        conn.close()

# Search Items
def search_items_db(filters: Dict[str, Any]) -> tuple[list[Dict[str, Any]], int]:
    """
    Search items (lost or found) based on filters.
    Supported filters: category, item_type, color, brand, status, query, limit, offset.
    Returns (items, total_count).
    """
    status = filters.get("status", "found") # Default to found items
    
    # Common filter building logic
    if status == "lost":
        base_cond = "status IN ('lost', 'reported_lost')"
        params = []
    else:
        base_cond = "status = ?"
        params = [status]

    if filters.get("category"):
        base_cond += " AND category = ?"
        params.append(filters["category"])
    
    if filters.get("item_type"):
        base_cond += " AND item_type = ?"
        params.append(filters["item_type"])

    if filters.get("color"):
        base_cond += " AND color = ?"
        params.append(filters["color"])

    if filters.get("brand"):
        base_cond += " AND brand = ?"
        params.append(filters["brand"])

    if filters.get("query"):
        base_cond += " AND (public_description LIKE ? OR category LIKE ? OR item_type LIKE ?)"
        like_val = f"%{filters['query']}%"
        params.extend([like_val, like_val, like_val])

    where_clause = f"WHERE {base_cond}"

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        limit = validate_int(filters.get("limit", 20), "limit", min_val=1, max_val=100)
        offset = validate_int(filters.get("offset", 0), "offset", min_val=0)

        if status in ["returned", "lost"]:
            # UNION query to cover both found and lost items
            # For 'lost' status, found_items uses status='lost', lost_items uses status='reported_lost'
            if status == "lost":
                found_where = where_clause
                lost_where = where_clause.replace("status IN ('lost', 'reported_lost')", "status = 'reported_lost'")
                # Adjust params for lost_where since it doesn't need 'lost' or 'reported_lost' in IN clause
                # Wait, my where_clause building was a bit simplified. Let's be precise.
                pass 
            
            # Rethink: The simplest way is to build independent where clauses for both.
            cond_found = "status = 'lost'" if status == "lost" else "status = 'returned'"
            cond_lost = "status = 'reported_lost'" if status == "lost" else "status = 'returned'"
            
            p_common = []
            c_common = ""
            for k in ["category", "item_type", "color", "brand"]:
                if filters.get(k):
                    c_common += f" AND {k} = ?"
                    p_common.append(filters[k])
            
            if filters.get("query"):
                c_common += " AND (public_description LIKE ? OR category LIKE ? OR item_type LIKE ?)"
                lv = f"%{filters['query']}%"
                p_common.extend([lv, lv, lv])

            count_query = f"""
                SELECT SUM(cnt) FROM (
                    SELECT COUNT(*) as cnt FROM found_items WHERE {cond_found} {c_common}
                    UNION ALL
                    SELECT COUNT(*) as cnt FROM lost_items WHERE {cond_lost} {c_common}
                )
            """
            cursor.execute(count_query, p_common * 2)
            total_count = cursor.fetchone()[0] or 0
            
            limit = validate_int(filters.get("limit", 20), "limit", min_val=1, max_val=100)
            offset = validate_int(filters.get("offset", 0), "offset", min_val=0)

            select_query = f"""
                SELECT id, report_id, category, item_type, color, brand,
                       found_location AS location, found_datetime AS incident_date,
                       public_description, main_picture, status, created_at, resolved_at,
                       'found' as source_table
                FROM found_items WHERE {cond_found} {c_common}
                UNION ALL
                SELECT id, report_id, category, item_type, color, brand,
                       last_seen_location AS location, last_seen_datetime AS incident_date,
                       public_description, main_picture, status, created_at, resolved_at,
                       'lost' as source_table
                FROM lost_items WHERE {cond_lost} {c_common}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(select_query, p_common * 2 + [limit, offset])

        else:
            # Traditional single-table search (for 'found' or 'pending_approval' etc)
            table = "found_items" if status == "found" else "lost_items"
            cursor.execute(f"SELECT COUNT(*) FROM {table} {where_clause}", params)
            total_count = cursor.fetchone()[0]
            
            limit = validate_int(filters.get("limit", 20), "limit", min_val=1, max_val=100)
            offset = validate_int(filters.get("offset", 0), "offset", min_val=0)

            select_query = f"SELECT * FROM {table} {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?"
            cursor.execute(select_query, params + [limit, offset])

        rows = cursor.fetchall()
        items = [dict(row) for row in rows]
        return items, total_count
    finally:
        conn.close()

def resolve_item_db(item_id, recipient_name, handover_notes, admin_username, claim_id=None, recipient_id=None, turnover_proof=None):
    """Marks a found item as returned and logs the handover."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        
        # 1. Update found_items status to 'returned' (Released)
        cursor.execute(
            """UPDATE found_items 
               SET status = 'returned', 
                   recipient_name = ?, 
                   recipient_id = ?, 
                   resolved_at = ?,
                   turnover_proof = ? 
               WHERE id = ?""",
            (recipient_name, recipient_id, now, turnover_proof, item_id)
        )
        
        updated_table = "found_item"
        if cursor.rowcount == 0:
            cursor.execute(
                """UPDATE lost_items 
                   SET status = 'returned',
                       recipient_name = ?, 
                       recipient_id = ?, 
                       resolved_at = ?,
                       turnover_proof = ?  
                   WHERE id = ?""",
                (recipient_name, recipient_id, now, turnover_proof, item_id)
            )
            if cursor.rowcount == 0:
                return {"error": f"Item {item_id} not found"}, 404
            updated_table = "lost_item"
        
        # 2. If a claim_id is provided, mark it as 'completed'
        if claim_id:
            cursor.execute(
                """UPDATE claims 
                   SET decision = 'completed', 
                       handover_notes = ?, 
                       completed_at = ? 
                   WHERE id = ?""",
                (f"ID: {recipient_id} | {handover_notes}", now, claim_id)
            )
        
        conn.commit()
        log_action("resolve_item", updated_table, item_id, admin_username, notes=f"Recipient: {recipient_name} ({recipient_id}) | Notes: {handover_notes}")
        return {"message": "Item marked as returned successfully"}, 200
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}, 500
    finally:
        conn.close()

def get_item_universal_db(identifier):
    """Fetch an item by its unique UUID report_id OR its integer ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Check if identifier is integer
        is_int = False
        try:
            int_id = int(identifier)
            is_int = True
        except:
            pass

        # Search lost_items
        if is_int:
            cursor.execute("SELECT *, 'lost' as type FROM lost_items WHERE id = ?", (int_id,))
        else:
            cursor.execute("SELECT *, 'lost' as type FROM lost_items WHERE report_id = ?", (identifier,))
        
        row = cursor.fetchone()
        if row: return dict(row)
        
        # Search found_items
        if is_int:
            cursor.execute("SELECT *, 'found' as type FROM found_items WHERE id = ?", (int_id,))
        else:
            cursor.execute("SELECT *, 'found' as type FROM found_items WHERE report_id = ?", (identifier,))
            
        row = cursor.fetchone()
        if row: return dict(row)
        
        return None
    finally:
        conn.close()
