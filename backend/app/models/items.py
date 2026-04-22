import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy import text
from ..extensions import db
from .validators import ValidationError, require_fields, validate_int
from .audit import log_action
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Lost Items
def create_lost_item(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a lost item record with validation and logging."""
    try:
        require_fields(data, ["category", "last_seen_location", "last_seen_datetime"])

        query = text("""
            INSERT INTO lost_items (
                report_id, category, item_type, last_seen_location,
                last_seen_datetime, public_description, private_details,
                main_picture, additional_picture_1, additional_picture_2,
                additional_picture_3, reporter_id, status, created_at
            )
            VALUES (:report_id, :cat, :type, :loc, :dt, :pub, :priv, :m_pic, :p1, :p2, :p3, :rep_id, :status, :now)
            RETURNING id
        """)
        
        params = {
            "report_id": str(uuid.uuid4()),
            "cat": data["category"],
            "type": data.get("item_type", "Unknown"),
            "loc": data["last_seen_location"],
            "dt": data["last_seen_datetime"],
            "pub": data.get("public_description"),
            "priv": data.get("private_details"),
            "m_pic": data.get("main_picture"),
            "p1": data.get("additional_picture_1"),
            "p2": data.get("additional_picture_2"),
            "p3": data.get("additional_picture_3"),
            "rep_id": data.get("reporter_id"),
            "status": "pending_approval",
            "now": datetime.now(timezone.utc)
        }
        
        result = db.session.execute(query, params)
        db.session.commit()
        row = result.fetchone()
        item_id = row[0] if row else None

        log_action("create", "lost_item", item_id, str(data.get("reporter_id", "system")))
        return {"message": "Lost item created successfully", "item_id": item_id}

    except ValidationError as ve:
        return {"error": ve.message}
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating lost item: {str(e)}")
        return {"error": "Internal server error while creating report."}

# Found Items
def create_found_item(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a found item record with validation and logging."""
    try:
        require_fields(data, ["category", "found_location", "found_datetime"])

        query = text("""
            INSERT INTO found_items (
                report_id, category, item_type, color, brand,
                found_location, found_datetime,
                public_description, private_details, main_picture,
                additional_picture_1, additional_picture_2, additional_picture_3,
                reporter_id, status, created_at
            )
            VALUES (:report_id, :cat, :type, :color, :brand, :loc, :dt, :pub, :priv, :m_pic, :p1, :p2, :p3, :rep_id, :status, :now)
            RETURNING id
        """)
        
        params = {
            "report_id": str(uuid.uuid4()),
            "cat": data["category"],
            "type": data.get("item_type", "Unknown"),
            "color": data.get("color"),
            "brand": data.get("brand"),
            "loc": data["found_location"],
            "dt": data["found_datetime"],
            "pub": data.get("public_description"),
            "priv": data.get("private_details"),
            "m_pic": data.get("main_picture"),
            "p1": data.get("additional_picture_1"),
            "p2": data.get("additional_picture_2"),
            "p3": data.get("additional_picture_3"),
            "rep_id": data.get("reporter_id"),
            "status": "pending_approval",
            "now": datetime.now(timezone.utc)
        }
        
        result = db.session.execute(query, params)
        db.session.commit()
        row = result.fetchone()
        item_id = row[0] if row else None

        log_action("create", "found_item", item_id, str(data.get("reporter_id", "system")))
        return {"message": "Found item created successfully", "item_id": item_id}

    except ValidationError as ve:
        return {"error": ve.message}
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating found item: {str(e)}")
        return {"error": "Internal server error while creating report."}

# Get Found Items
def get_published_found_items(limit=20, offset=0, categories=None) -> tuple[list[Dict[str, Any]], int]:
    """
    Return all published found items with pagination.
    """
    where_clause = "WHERE status = 'found'"
    params = {"limit": limit, "offset": offset}
    
    if categories:
        if isinstance(categories, list):
            placeholders = ",".join([f":c{i}" for i in range(len(categories))])
            where_clause += f" AND category IN ({placeholders})"
            for i, cat in enumerate(categories):
                params[f"c{i}"] = cat
        else:
            where_clause += " AND category = :category"
            params["category"] = categories

    count_query = text(f"SELECT COUNT(*) FROM found_items {where_clause}")
    total_count = db.session.execute(count_query, params).scalar()

    select_query = text(f"""
        SELECT id, report_id, category, item_type, color, brand,
               found_location, found_datetime, public_description,
               main_picture, reporter_id
        FROM found_items
        {where_clause}
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    result = db.session.execute(select_query, params).fetchall()
    items = [dict(row._mapping) for row in result]
    return items, total_count

def get_found_item_by_id(item_id: int) -> Optional[Dict[str, Any]]:
    validate_int(item_id, "item_id")
    query = text("SELECT * FROM found_items WHERE id = :id")
    row = db.session.execute(query, {"id": item_id}).fetchone()
    return dict(row._mapping) if row else None

def verify_report_db(report_id, entity_type, decision, reason, admin_username):
    table = "lost_items" if entity_type == "lost" else "found_items"
    approved_status = "reported_lost" if entity_type == "lost" else "found"
    new_status = approved_status if decision == "approved" else "rejected"

    query = text(f"UPDATE {table} SET status = :status, rejection_reason = :reason WHERE id = :id")
    res = db.session.execute(query, {"status": new_status, "reason": reason, "id": report_id})
    if res.rowcount == 0:
        return {"error": f"Report ID {report_id} not found."}, 404
    
    db.session.commit()
    log_action(f"verify_report_{decision}", entity_type, report_id, admin_username, notes=reason)
    return {"message": f"Report {decision} successfully"}, 200

def get_user_reports_db(user_id):
    l_query = text("SELECT *, last_seen_datetime AS incident_date, created_at AS report_date, 'lost' as type FROM lost_items WHERE reporter_id = :uid AND (is_dismissed = FALSE OR is_dismissed IS NULL)")
    f_query = text("SELECT *, found_datetime AS incident_date, created_at AS report_date, 'found' as type FROM found_items WHERE reporter_id = :uid AND (is_dismissed = FALSE OR is_dismissed IS NULL)")
    
    lost = [dict(row._mapping) for row in db.session.execute(l_query, {"uid": user_id}).fetchall()]
    found = [dict(row._mapping) for row in db.session.execute(f_query, {"uid": user_id}).fetchall()]
    return lost + found

def dismiss_report_db(report_id, entity_type, user_id):
    table = "lost_items" if entity_type == "lost" else "found_items"
    query = text(f"UPDATE {table} SET is_dismissed = TRUE WHERE id = :id AND reporter_id = :uid")
    db.session.execute(query, {"id": report_id, "uid": user_id})
    db.session.commit()
    return {"message": "Report dismissed successfully"}, 200

# Search Items
def search_items_db(filters: Dict[str, Any]) -> tuple[list[Dict[str, Any]], int]:
    status = filters.get("status", "found")
    limit = validate_int(filters.get("limit", 20), "limit", min_val=1, max_val=100)
    offset = validate_int(filters.get("offset", 0), "offset", min_val=0)
    
    # Common filter building
    c_common = ""
    params = {"limit": limit, "offset": offset}
    for k in ["category", "item_type", "color", "brand"]:
        if filters.get(k):
            c_common += f" AND {k} = :{k}"
            params[k] = filters[k]
    
    if filters.get("query"):
        c_common += " AND (public_description LIKE :q OR category LIKE :q OR item_type LIKE :q)"
        params["q"] = f"%{filters['query']}%"

    if status in ["returned", "lost"]:
        cond_found = "status = 'found'" if status == "lost" else "status = 'returned'"
        cond_lost = "status = 'reported_lost'" if status == "lost" else "status = 'returned'"
        
        count_query = text(f"""
            SELECT (SELECT COUNT(*) FROM found_items WHERE {cond_found} {c_common}) + 
                   (SELECT COUNT(*) FROM lost_items WHERE {cond_lost} {c_common})
        """)
        total_count = db.session.execute(count_query, params).scalar() or 0
        
        select_query = text(f"""
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
            LIMIT :limit OFFSET :offset
        """)
        result = db.session.execute(select_query, params).fetchall()
    else:
        table = "found_items" if status == "found" else "lost_items"
        where_clause = f"WHERE status = :status {c_common}"
        params["status"] = status
        
        count_query = text(f"SELECT COUNT(*) FROM {table} {where_clause}")
        total_count = db.session.execute(count_query, params).scalar() or 0
        
        select_query = text(f"SELECT * FROM {table} {where_clause} ORDER BY created_at DESC LIMIT :limit OFFSET :offset")
        result = db.session.execute(select_query, params).fetchall()

    return [dict(row._mapping) for row in result], total_count

def resolve_item_db(item_id, recipient_name, handover_notes, admin_username, claim_id=None, recipient_id=None, turnover_proof=None):
    try:
        now = datetime.now(timezone.utc)
        params = {
            "name": recipient_name,
            "rid": recipient_id,
            "now": now,
            "proof": turnover_proof,
            "id": item_id
        }

        # 1. Fetch item details to migrate
        item = get_item_universal_db(item_id)
        if not item:
            return {"error": "Item not found"}, 404
            
        source_table = item.get("type", "found")
        original_report_id = item.get("report_id")
        category = item.get("category")
        item_type = item.get("item_type")

        # Snapshot fields to store in released_items
        main_picture = item.get("main_picture")
        public_description = item.get("public_description")
        color = item.get("color")
        brand = item.get("brand")
        last_seen_location = item.get("last_seen_location")
        found_location = item.get("found_location")

        # 2. Update original record status
        table_name = "found_items" if source_table == "found" else "lost_items"
        db.session.execute(text(f"""
            UPDATE {table_name} SET status = 'returned', recipient_name = :name, recipient_id = :rid, 
            resolved_at = :now, turnover_proof = :proof WHERE id = :id
        """), params)

        # 3. Create record in released_items table (with visual snapshot)
        db.session.execute(text("""
            INSERT INTO released_items (
                original_report_id, item_source, category, item_type,
                claimant_name, recipient_id, released_by_admin,
                handover_notes, turnover_proof,
                color, brand, main_picture, public_description,
                last_seen_location, found_location,
                resolved_at
            )
            VALUES (
                :o_rid, :src, :cat, :type,
                :c_name, :r_id, :admin,
                :notes, :proof,
                :color, :brand, :m_pic, :pub_desc, :last_loc, :found_loc,
                :now
            )
        """), {
            "o_rid": original_report_id,
            "src": source_table,
            "cat": category,
            "type": item_type,
            "c_name": recipient_name,
            "r_id": recipient_id,
            "admin": admin_username,
            "notes": handover_notes,
            "proof": turnover_proof,
            "color": color,
            "brand": brand,
            "m_pic": main_picture,
            "pub_desc": public_description,
            "last_loc": last_seen_location,
            "found_loc": found_location,
            "now": now
        })
        
        if claim_id:
            db.session.execute(text("""
                UPDATE claims SET decision = 'completed', handover_notes = :notes, completed_at = :now WHERE id = :cid
            """), {"notes": f"ID: {recipient_id} | {handover_notes}", "now": now, "cid": claim_id})
        
        db.session.commit()
        log_action("resolve_item", source_table, item_id, admin_username, notes=f"Recipient: {recipient_name} ({recipient_id})")
        return {"message": "Item marked as returned and moved to released storage successfully"}, 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resolving item: {str(e)}")
        return {"error": f"Failed to resolve item: {str(e)}"}, 500

def get_released_items_db(limit=20, offset=0, query=None):
    """Fetch items from the dedicated released_items table."""
    where_clause = ""
    params = {"limit": limit, "offset": offset}

    if query:
        where_clause = "WHERE claimant_name LIKE :q OR category LIKE :q OR item_type LIKE :q"
        params["q"] = f"%{query}%"

    count_query = text(f"SELECT COUNT(*) FROM released_items {where_clause}")
    total = db.session.execute(count_query, params).scalar() or 0

    select_query = text(f"""
        SELECT * FROM released_items 
        {where_clause} 
        ORDER BY resolved_at DESC 
        LIMIT :limit OFFSET :offset
    """)
    result = db.session.execute(select_query, params).fetchall()
    return [dict(row._mapping) for row in result], total


def get_released_item_by_original_id_db(original_report_id: str):
    """Fetch a single released item snapshot by original_report_id (lost/found report_id)."""
    query = text("""
        SELECT * FROM released_items
        WHERE original_report_id = :rid
        ORDER BY resolved_at DESC
        LIMIT 1
    """)
    row = db.session.execute(query, {"rid": original_report_id}).fetchone()
    return dict(row._mapping) if row else None

def get_item_universal_db(identifier):
    try:
        int_id = int(identifier)
        params = {"id": int_id}
        l_q = text("SELECT *, 'lost' as type FROM lost_items WHERE id = :id")
        f_q = text("SELECT *, 'found' as type FROM found_items WHERE id = :id")
    except:
        params = {"rid": identifier}
        l_q = text("SELECT *, 'lost' as type FROM lost_items WHERE report_id = :rid")
        f_q = text("SELECT *, 'found' as type FROM found_items WHERE report_id = :rid")

    row = db.session.execute(l_q, params).fetchone()
    if row: return dict(row._mapping)
    row = db.session.execute(f_q, params).fetchone()
    if row: return dict(row._mapping)
    return None

def get_pending_reports_db():
    l_q = text("SELECT *, 'lost' as type FROM lost_items WHERE status = 'pending_approval'")
    f_q = text("SELECT *, 'found' as type FROM found_items WHERE status = 'pending_approval'")
    lost = [dict(row._mapping) for row in db.session.execute(l_q).fetchall()]
    found = [dict(row._mapping) for row in db.session.execute(f_q).fetchall()]
    return {"pending": lost + found}

def get_dashboard_stats_db():
    total_lost = db.session.execute(text("SELECT COUNT(*) FROM lost_items WHERE status = 'reported_lost'")).scalar() or 0
    total_found = db.session.execute(text("SELECT COUNT(*) FROM found_items WHERE status = 'found'")).scalar() or 0
    pending_claims = db.session.execute(text("SELECT COUNT(*) FROM claims WHERE decision = 'pending'")).scalar() or 0
    resolved = db.session.execute(text("SELECT COUNT(*) FROM released_items")).scalar() or 0
    
    return {
        "total_lost": total_lost,
        "total_found": total_found,
        "pending_claims": pending_claims,
        "resolved_items": resolved
    }
